from pathlib import Path

ROOT = Path("source")

def replace_once(path, old, new):
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one patch point in {path}, found {count}: {old[:100]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")

# Give the experimental build its own identity so it installs beside the user's
# original MeloNX app. The RamDonor extension follows the experimental app ID.
old_id = "com.flyingsquirrel0419.MeloNX"
new_id = "com.stossy11.MeloNX.Experimental"
for file in (ROOT / "src/MeloNX").rglob("*"):
    if not file.is_file() or file.stat().st_size > 2_000_000:
        continue
    try:
        text = file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    if old_id in text:
        file.write_text(text.replace(old_id, new_id), encoding="utf-8")

# Enable the persistent shader cache by default in fresh experimental configurations.
# Keep async compilation off for this first controlled change; it remains opt-in.
replace_once(
    "src/MeloNX/MeloNX/Core/Models/Options/Options.swift",
    "    var disableShaderCache: Bool = true",
    "    var disableShaderCache: Bool = false",
)
replace_once(
    "src/MeloNX/MeloNX/Core/Models/Options/Options+Codable.swift",
    "disableShaderCache         = try c.decodeIfPresent(Bool.self,   forKey: .disableShaderCache)       ?? true",
    "disableShaderCache         = try c.decodeIfPresent(Bool.self,   forKey: .disableShaderCache)       ?? false",
)

# Enable async shader/pipeline compilation by default for the next controlled experiment.
# Keep this as a user setting; do not force it on for existing installations.
replace_once(
    "src/MeloNX/MeloNX/Core/Models/Options/Options.swift",
    "    var enableAsyncShaderCompilation: Bool = false",
    "    var enableAsyncShaderCompilation: Bool = true",
)
replace_once(
    "src/MeloNX/MeloNX/Core/Models/Options/Options+Codable.swift",
    "enableAsyncShaderCompilation = try c.decodeIfPresent(Bool.self, forKey: .enableAsyncShaderCompilation) ?? false",
    "enableAsyncShaderCompilation = try c.decodeIfPresent(Bool.self, forKey: .enableAsyncShaderCompilation) ?? true",
)

# Capture diagnostics even if the user's normal logging preferences are quiet.
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            Logger.SetEnable(LogLevel.Debug, option.LoggingEnableDebug);",
    "            Logger.SetEnable(LogLevel.Debug, option.LoggingEnableDebug); // Avoid forcing verbose logs in performance tests\n"
    "            Logger.SetEnable(LogLevel.Error, true);\n"
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: MeloNX 2.7 diagnostic build starting.\");"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            Logger.RestartTime();",
    "            Logger.RestartTime();\n"
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: LoadApplication entered.\");"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            _emulationContext = InitializeEmulationContext(window, renderer, options);",
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: initializing emulation context.\");\n"
    "            _emulationContext = InitializeEmulationContext(window, renderer, options);\n"
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: emulation context initialized.\");"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            if (Directory.Exists(path))",
    "            Logger.Notice.Print(LogClass.Application, $\"DIAGNOSTICS: loading game content from '{path}'.\");\n\n"
    "            if (Directory.Exists(path))"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "                        if (!_emulationContext.LoadNsp(path)) { _emulationContext.Dispose(); return false; }",
    "                        Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: entering LoadNsp.\");\n"
    "                        if (!_emulationContext.LoadNsp(path)) { _emulationContext.Dispose(); return false; }\n"
    "                        Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: LoadNsp returned successfully.\");"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            SetupProgressHandler();\n            ExecutionEntrypoint();\n            return true;",
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: game content loaded; attaching PTC/shader progress handlers.\");\n"
    "            SetupProgressHandler();\n"
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: entering execution entrypoint.\");\n"
    "            ExecutionEntrypoint();\n"
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: execution entrypoint returned.\");\n"
    "            return true;"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            _window.Initialize(_emulationContext, _inputConfiguration, _enableKeyboard, _enableMouse);\n"
    "            _window.Execute();",
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: initializing emulation window.\");\n"
    "            _window.Initialize(_emulationContext, _inputConfiguration, _enableKeyboard, _enableMouse);\n"
    "            Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: emulation window initialized; entering Execute.\");\n"
    "            _window.Execute();"
)
replace_once(
    "src/Ryujinx.Library/Library.cs",
    "            return GameInfoLoader.GetGameInfoNative(_virtualFileSystem, stream, extension);",
    "            Logger.Info?.Print(LogClass.Application, $\"DIAGNOSTICS: GetGameInfo started for {extension}.\");\n"
    "            var result = GameInfoLoader.GetGameInfoNative(_virtualFileSystem, stream, extension);\n"
    "            Logger.Info?.Print(LogClass.Application, \"DIAGNOSTICS: GetGameInfo completed.\");\n"
    "            return result;"
)

# A UI-thread heartbeat proves whether the host loop remains responsive.
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "        public void MainLoop()\n        {\n            while (_isActive)",
    "        public void MainLoop()\n        {\n"
    "            long diagnosticLastHeartbeat = Stopwatch.GetTimestamp();\n"
    "            while (_isActive)"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                _inputUpdatedEvent.WaitOne(1);\n            }\n\n            _exitEvent.Set();",
    "                _inputUpdatedEvent.WaitOne(1);\n"
    "                if (Stopwatch.GetElapsedTime(diagnosticLastHeartbeat).TotalSeconds >= 5)\n"
    "                {\n"
    "                    Logger.Notice.Print(LogClass.Application, \"DIAGNOSTICS: UI/main-loop heartbeat; host event loop is alive.\");\n"
    "                    diagnosticLastHeartbeat = Stopwatch.GetTimestamp();\n"
    "                }\n"
    "            }\n\n            _exitEvent.Set();"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "        public void Render()\n        {\n            InitializeWindowRenderer();\n\n            Device.Gpu.Renderer.Initialize(_glLogLevel);\n\n            InitializeRenderer();",
    "        public void Render()\n        {\n"
    "            Logger.Notice.Print(LogClass.Gpu, \"DIAGNOSTICS: render thread entered; initializing window renderer.\");\n"
    "            InitializeWindowRenderer();\n"
    "            Logger.Notice.Print(LogClass.Gpu, \"DIAGNOSTICS: window renderer initialized; initializing GPU renderer.\");\n"
    "            Device.Gpu.Renderer.Initialize(_glLogLevel);\n"
    "            Logger.Notice.Print(LogClass.Gpu, \"DIAGNOSTICS: GPU renderer initialized; initializing window surface.\");\n"
    "            InitializeRenderer();\n"
    "            Logger.Notice.Print(LogClass.Gpu, \"DIAGNOSTICS: window surface initialized.\");"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "            Device.Gpu.Renderer.RunLoop(() =>\n            {\n                Device.Gpu.SetGpuThread();\n                Device.Gpu.InitializeShaderCache(_gpuCancellationTokenSource.Token);\n\n                while (_isActive)",
    "            Device.Gpu.Renderer.RunLoop(() =>\n            {\n"
    "                Device.Gpu.SetGpuThread();\n"
    "                Logger.Notice.Print(LogClass.Gpu, \"DIAGNOSTICS: shader cache initialization started.\");\n"
    "                Device.Gpu.InitializeShaderCache(_gpuCancellationTokenSource.Token);\n"
    "                Logger.Notice.Print(LogClass.Gpu, \"DIAGNOSTICS: shader cache initialization completed; GPU loop started.\");\n"
    "                long diagnosticLastHeartbeat = Stopwatch.GetTimestamp();\n"
    "                long diagnosticFifoReady = 0;\n"
    "                long diagnosticFrames = 0;\n"
    "                long diagnosticPresents = 0;\n\n"
    "                while (_isActive)"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                    if (Device.WaitFifo())\n                    {\n                        Device.Statistics.RecordFifoStart();\n                        Device.ProcessFrame();\n                        Device.Statistics.RecordFifoEnd();\n                    }\n\n                    if (Device.PresentLoop(SwapBuffers))\n                    {",
    "                    bool fifoReady = Device.WaitFifo();\n"
    "                    if (fifoReady)\n"
    "                    {\n"
    "                        diagnosticFifoReady++;\n"
    "                        Device.Statistics.RecordFifoStart();\n"
    "                        Device.ProcessFrame();\n"
    "                        diagnosticFrames++;\n"
    "                        Device.Statistics.RecordFifoEnd();\n"
    "                    }\n\n"
    "                    if (Device.PresentLoop(SwapBuffers))\n"
    "                    {\n"
    "                        diagnosticPresents++;"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                    if (_ticks >= _ticksPerFrame)\n                    {",
    "                    if (Stopwatch.GetElapsedTime(diagnosticLastHeartbeat).TotalSeconds >= 5)\n"
    "                    {\n"
    "                        Logger.Notice.Print(LogClass.Gpu, $\"DIAGNOSTICS: GPU heartbeat; FIFO-ready={diagnosticFifoReady}, processed-frames={diagnosticFrames}, presents={diagnosticPresents}.\");\n"
    "                        diagnosticFifoReady = 0;\n"
    "                        diagnosticFrames = 0;\n"
    "                        diagnosticPresents = 0;\n"
    "                        diagnosticLastHeartbeat = Stopwatch.GetTimestamp();\n"
    "                    }\n\n"
    "                    if (_ticks >= _ticksPerFrame)\n                    {"
)

# Record whether the guest CPU ever enters its JIT dispatcher.
replace_once(
    "src/ARMeilleure/Translation/Translator.cs",
    "        private volatile int _threadCount;",
    "        private volatile int _threadCount;\n"
    "        private static int _diagnosticFirstGuestExecutionLogged;"
)
replace_once(
    "src/ARMeilleure/Translation/Translator.cs",
    "        public void Execute(State.ExecutionContext context, ulong address)\n        {\n            if (Interlocked.Increment(ref _threadCount) == 1)",
    "        public void Execute(State.ExecutionContext context, ulong address)\n        {\n"
    "            if (Interlocked.Exchange(ref _diagnosticFirstGuestExecutionLogged, 1) == 0)\n"
    "            {\n"
    "                Ryujinx.Common.Logging.Logger.Notice.Print(Ryujinx.Common.Logging.LogClass.Cpu, $\"DIAGNOSTICS: first guest CPU execution entered at 0x{address:X}.\");\n"
    "            }\n\n"
    "            if (Interlocked.Increment(ref _threadCount) == 1)"
)

print("Applied MeloNX 2.7 experimental identity and startup/CPU/GPU diagnostics patches.")
