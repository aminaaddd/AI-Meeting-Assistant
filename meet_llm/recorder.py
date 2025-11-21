import os
import time
import threading
import sounddevice as sd
import soundfile as sf
from typing import Optional


class AlternatingRecorder:
    """Single input stream that writes audio into two alternating WAV files with minimal gap.

    Usage:
      rec = AlternatingRecorder(device_index=None, channels=1)
      rec.start_stream()
      # run alternate_recording in background thread, it will put finished filenames into a queue
    """

    def __init__(self, device_index: Optional[int] = None, samplerate: Optional[int] = None, channels: int = 1):
        self.device_index = device_index
        self.channels = channels
        self._stream: Optional[sd.InputStream] = None
        self.samplerate = samplerate

        # writers for slot 0 and 1
        self._writers = [None, None]
        self._writers_lock = threading.Lock()
        self._active_slot = None

        # pick device/samplerate now
        dev = sd.query_devices()
        if device_index is not None:
            dev_info = sd.query_devices(device_index)
        else:
            # pick first input-capable device
            dev_info = None
            for i, d in enumerate(dev):
                if d.get("max_input_channels", 0) > 0:
                    dev_info = d
                    self.device_index = i
                    break
            if dev_info is None:
                raise RuntimeError("No input device available")

        if self.samplerate is None:
            try:
                self.samplerate = int(dev_info.get("default_samplerate", 16000))
            except Exception:
                self.samplerate = 16000

        # prepare input stream (callback will dispatch frames to active writer)
        self._stream = sd.InputStream(device=self.device_index, channels=self.channels,
                                      samplerate=self.samplerate, dtype="float32",
                                      callback=self._callback)

    def start_stream(self):
        if self._stream is None:
            raise RuntimeError("Stream not initialized")
        if not self._stream.active:
            self._stream.start()

    def stop_stream(self):
        if self._stream is not None and self._stream.active:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _callback(self, indata, frames, time_info, status):
        # called in audio thread
        if status:
            # print status to help debugging (non-blocking)
            print(f"Recorder status: {status}")
        with self._writers_lock:
            slot = self._active_slot
            if slot is not None and self._writers[slot] is not None:
                try:
                    # indata is float32 numpy array shape (frames, channels)
                    self._writers[slot].write(indata)
                except Exception as e:
                    print(f"Error writing audio: {e}")

    def _open_writer(self, slot: int, filepath: str):
        # open soundfile for writing (will convert floats to PCM16)
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        sfw = sf.SoundFile(filepath, mode="w", samplerate=self.samplerate, channels=self.channels, subtype="PCM_16")
        with self._writers_lock:
            self._writers[slot] = sfw

    def _close_writer(self, slot: int):
        with self._writers_lock:
            w = self._writers[slot]
            self._writers[slot] = None
        if w is not None:
            try:
                w.flush()
                w.close()
            except Exception:
                pass

    def alternate_recording(self, seconds_per_chunk: int, out_dir: str, base_name: str, out_queue, stop_event: threading.Event):
        """Run an alternating recording loop in the current thread; when a chunk finishes it will be
        placed into out_queue. This method blocks until stop_event is set.
        """
        slot = 0
        counter = 0
        # first writer
        prev_filename = None

        try:
            while not stop_event.is_set():
                filename = os.path.join(out_dir, f"{base_name}_{slot}_{counter}.wav")
                # open next writer first
                self._open_writer(slot, filename)

                # switch active slot immediately so incoming frames go to it
                with self._writers_lock:
                    prev_slot = 1 - slot
                    self._active_slot = slot

                # if there was a previously open writer (the other slot), close it and enqueue its file
                if prev_filename is not None:
                    # close the previous slot writer (which is prev_slot)
                    self._close_writer(prev_slot)
                    try:
                        out_queue.put(prev_filename)
                    except Exception:
                        print("Warning: failed to put filename into queue")

                # keep this writer for the requested duration
                start = time.time()
                while (time.time() - start) < seconds_per_chunk and not stop_event.is_set():
                    time.sleep(0.1)

                # prepare to rotate: next slot becomes active in next loop iteration
                prev_filename = filename
                slot = 1 - slot
                counter += 1

        finally:
            # close any open writers
            self._active_slot = None
            self._close_writer(0)
            self._close_writer(1)
            # if last file exists and wasn't enqueued, enqueue it
            try:
                if prev_filename is not None:
                    out_queue.put(prev_filename)
            except Exception:
                pass
