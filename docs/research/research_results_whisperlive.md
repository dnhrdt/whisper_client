# WhisperLive Research Findings
Version: 1.0
Timestamp: 2025-02-27 14:41 CET

Based on the research in the `docs/research/WhisperLive` directory, here are some key takeaways:

**1. Audio Handling and Resampling:**

*   **Client-Side Resampling:** The `algoman01-transcription-app.txt` repository includes a `resampleTo16kHZ` function in `+page.svelte`, indicating that the client is responsible for resampling audio to 16kHz. This suggests that we need to implement robust client-side resampling.
*   **System Audio Capture:** The `qasax-whisperlive-systemaudio` repository uses the `soundcard` library for capturing system audio, offering cross-platform compatibility. This could be a solution for capturing audio from various applications.

**2. Server Configuration and Backends:**

*   **Backend Options:** The `collabora-whisperlive.txt` repository highlights the use of `faster_whisper` and `tensorrt` backends. This suggests that we should focus on these two backends for our project.
*   **TensorRT Optimization:** The `collabora-whisperfusion.txt` repository emphasizes the use of TensorRT for optimizing Whisper and LLMs, potentially improving performance.
*   **OpenMP Thread Control:** The `collabora-whisperlive.txt` repository allows controlling the number of threads used by OpenMP using the `--omp_num_threads` argument, which is useful for managing CPU resources.
*   **Single Model Mode:** The `collabora-whisperlive.txt` repository supports a single model mode, which can reduce memory usage.

**3. WebSocket Communication:**

*   **WebSocket URL Configuration:** The `.env.example` file in `algoman01-transcription-app` shows how to configure the WebSocket URL. This highlights the importance of a configurable client.

**4. Code Snippets and Implementation Details:**

*   **TensorRT Build Scripts:** The `docker/scripts` directory in `collabora-whisperfusion` contains scripts for building Whisper and Mistral/Phi TensorRT engines. These scripts could provide valuable information on how to build and configure TensorRT for Whisper.
*   **Client Implementation:** The `run_client.py` file in `qasax-whisperlive-systemaudio` shows how to initialize the `TranscriptionClient` with the `wasapi=True` option for system audio capture.
