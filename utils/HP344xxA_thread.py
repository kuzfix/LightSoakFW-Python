import atexit
import threading
import time
from datetime import datetime
from typing import Tuple, Optional
from pymeasure.instruments.agilent import Agilent34410A
from pymeasure.instruments.hp import HP34401A
import pyvisa

class A34401AMeasurementWorker:
    """Thread-safe worker for slow Agilent A34401A measurements"""
    
    def __init__(self,model = None, resource = None):
        self.result: Optional[float] = None
        self.timestamp: Optional[datetime] = None
        self.is_new = False
        self.should_be_running = False
        self.has_stopped = True
        self.lock = threading.Lock()
        # For error handling
        self.last_error: Optional[str] = None
        self.dmm = None
        self.initOK = False
        self.resource = resource
        self._close_lock = threading.Lock()
        self._closed = False
        atexit.register(self.stop)
        if model is not None:
            self.init_instrument(model)

    def setVisaResource(self,resource):
        self.resource = resource

    def init_instrument(self, model = "34401A") -> int:
        if self.resource is None:
            visa_resources = self.get_visa_resources()
            if visa_resources is None:
                return -1
            self.resource = visa_resources[0]
        if model == "34401A":
            try:
                self.dmm = HP34401A(self.resource, timeout=7000)
                self._closed = False
                self.dmm.write("*RST")
                self.dmm.write("*CLS")      # Clear status to avoid old errors
                self.dmm.write("SYST:REM")  # Required by A34401A, but not by A34410A.
                self.dmm.write("CONF:FRES 100000")  # 4-wire resistance
                self.dmm.write("FRES:NPLC 100")    # higher NPLC = better noise performance
                self.dmm.write("TRIG:SOUR IMM")
                self.initOK = True
            except Exception as e:
                print(f"  HP34401A Init Error: {e}")
            return 0
        elif model == "34410A":
            try:
                self.dmm = Agilent34410A(self.resource, timeout=7000)
                self._closed = False
                self.dmm.write("*RST")
                self.dmm.write("*CLS")      # Clear status to avoid old errors
                #self.dmm.write("SYST:REM")  # Required by A34401A, but not by A34410A.
                self.dmm.write("CONF:FRES 100000")  # 4-wire resistance
                self.dmm.write("FRES:NPLC 100")    # higher NPLC = better noise performance
                self.dmm.write("TRIG:SOUR IMM")
                self.initOK = True
            except Exception as e:
                print(f"  A34410A Init Error: {e}")
            return 0
        return -2 # Unknown instrument

    def get_visa_resources(self):
        rm_py = None
        resources_py = None
        try:
            rm_py = pyvisa.ResourceManager('@py')
            resources_py = rm_py.list_resources()
            if resources_py:
                for r in resources_py:
                    print(f"  {r}")
            else:
                print("  None found.")
        except Exception as e:
            print(f"  Error: {e}")
        finally:
            if rm_py is not None:
                try:
                    rm_py.close()
                except Exception:
                    pass
        if resources_py:
            return resources_py
        else:
            return None

    def _close_instrument(self):
        if self._closed:
            return
        with self._close_lock:
            now = time.time()
            if self.should_be_running:
                self.should_be_running = False  # Signal measurement loop to stop
            while not self.has_stopped:
                if time.time() - now > 6:  # Timeout after 5 seconds
                    print("  Warning: Instrument close timeout. Forcing shutdown.")
                    break
                time.sleep(0.1)  # to prevent processor spin-loop
            self.dmm.shutdown()  # Properly close the instrument
            self.dmm.adapter.manager.close()  # Ensure VISA connection is closed
            self.initOK = False
            self._closed = True

    def _take_measurement(self) -> float:
        if self.dmm is None:
            raise RuntimeError("Instrument is not initialized")
        reading = float(self.dmm.ask("READ?"))  # takes 4s at NPLC = 4s
        #print(f"4W Resistance: {reading:.6f} ohm")
        temperature = self.pt1000_resistance_to_temperature_c(reading)
        return temperature

    def measurement_loop(self):
        """Run this in separate thread - handles continuous measurements"""
        self.should_be_running = True
        self.has_stopped = False
        time.sleep(1)  # Short delay to ensure settings take effect
        while self.should_be_running:
            try:
                if self.initOK:
                    result = self._take_measurement()
                else:
                    result = -999  # fail silently with impossible value
                    time.sleep(4)
                    continue
                
                with self.lock:
                    self.result = result
                    self.timestamp = datetime.now()
                    self.is_new = True
                    self.last_error = None
                    
            except Exception as e:
                with self.lock:
                    self.last_error = str(e)
                print(f"HP344xxA Measurement error: {e}")
                self.should_be_running = False  # Stop on error, or you could choose to continue and retry
                self._close_instrument()
            # Small delay to prevent tight loop if any unhandled errors occur
            time.sleep(0.1)  #adjust based on expected measurement time
        self.has_stopped = True
          
    
        """
        Get latest measurement from main thread
        
        Returns:
            (value, is_new, timestamp)
            - value: The measurement or None if not yet available
            - is_new: True if this is the first retrieval of this result
            - timestamp: When the measurement was taken
        """
    def get_latest(self) -> Tuple[Optional[float], bool, Optional[datetime]]:
        with self.lock:
            is_new = self.is_new
            self.is_new = False  # Mark as consumed
            return self.result, is_new, self.timestamp
    
        """Fallback cleanup when object is garbage collected (e.g. cell re-run in Jupyter)."""
    def __del__(self):
        self._close_instrument()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def stop(self):
        """Gracefully stop the measurement thread"""
        self.should_be_running = False
        self._close_instrument()

    def pt1000_resistance_to_temperature_c(self, resistance_ohm: float) -> float:
        """Convert PT1000 resistance (ohm) to temperature (°C) using Newton iteration."""
        if resistance_ohm <= 0:
            #raise ValueError("Resistance must be > 0 ohm")
            return -9999  #do not raise any exceptions, instead fail silently and return impossibly low value

        R0 = 1000.0
        A = 3.9083e-3
        B = -5.775e-7
        C = -4.183e-12  # used for T < 0 °C
        # Good initial estimate near ambient
        t = (resistance_ohm / R0 - 1.0) / A

        for _ in range(30):
            if t >= 0:
                # R(T) = R0 * (1 + A*T + B*T^2)
                f = R0 * (1 + A * t + B * t * t) - resistance_ohm
                df = R0 * (A + 2 * B * t)
            else:
                # R(T) = R0 * (1 + A*T + B*T^2 + C*(T-100)*T^3)
                f = R0 * (1 + A * t + B * t * t + C * (t - 100) * t**3) - resistance_ohm
                df = R0 * (A + 2 * B * t + C * (4 * t**3 - 300 * t**2))

            dt = f / df
            t -= dt
            if abs(dt) < 1e-9:
                break

        return t


# Main program example
def main():
    # Initialize worker
    worker = A34401AMeasurementWorker()
    print("Available VISA resources:\n")
    visa_resources = worker.get_visa_resources()
    if not visa_resources:
        print("No VISA resources found.")
        return
    print()
    print("Initializing worker using the firt available VISA resource...")
    worker.setVisaResource(visa_resources[2])
    #worker.setVisaResource("USB0::2391::1543::MY47016751::0::INSTR")
    #worker.init_instrument("34410A")
    worker.init_instrument("34401A")
    
    # Start background thread (daemon=True means it stops with main program)
    measurement_thread = threading.Thread(
        target=worker.measurement_loop,
        name="A34401A-Measurement",
        daemon=True
    )
    measurement_thread.start()
    
    # Simulate main data recording loop
    Nloops = 10
    print(f"Starting example data collection (will end after {Nloops}s)...")
    print("-" * 60)
    
    try:
        for i in range(Nloops):  # Run for ~10 seconds
            # Your main program does other things here

            # When needed, get the latest measurement (non-blocking)
            value, is_new, timestamp = worker.get_latest()

            if is_new and value is not None and timestamp is not None:
                print(f"[{i}] NEW measurement: {value:.3f}°C at {timestamp.strftime('%H:%M:%S.%f')[:-3]}")

                # Store to database here

            else:
                if value is not None:
                    print(f"[{i}] (reusing previous: {value:.3f}°C)")
                else:
                    print(f"[{i}] (waiting for first measurement...)")

            # Main thread continues with other work
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        worker.stop()
        measurement_thread.join(timeout=7)  #measurement takes 4s, close timeout 6s +1s extra here
        print("\nData collection stopped.")

if __name__ == '__main__':
    main()