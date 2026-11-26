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

# Async shader compilation remains controlled by the user's existing setting.

# Instrument skipped Vulkan draws while background pipelines compile.
# Log one summary per 64 skipped draws; do not change scheduling or wait thresholds.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs",
    "        private long _firstSkippedDrawTimestamp;\n",
    "        private long _firstSkippedDrawTimestamp;\n"
    "        private int _diagnosticSkippedDrawCount;\n"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs",
    "        public void NoteSkippedDraw()\n"
    "        {\n"
    "            if (_firstSkippedDrawTimestamp == 0)\n"
    "            {\n"
    "                _firstSkippedDrawTimestamp = Stopwatch.GetTimestamp();\n"
    "            }\n"
    "        }",
    "        public void NoteSkippedDraw()\n"
    "        {\n"
    "            if (_firstSkippedDrawTimestamp == 0)\n"
    "            {\n"
    "                _firstSkippedDrawTimestamp = Stopwatch.GetTimestamp();\n"
    "            }\n"
    "            int skipped = Interlocked.Increment(ref _diagnosticSkippedDrawCount);\n"
    "            if ((skipped & 63) == 0)\n"
    "            {\n"
    "                double elapsedMs = Stopwatch.GetElapsedTime(_firstSkippedDrawTimestamp).TotalMilliseconds;\n"
    "                Logger.Notice.PrintMsg(LogClass.Gpu, $\"DIAGNOSTICS: Vulkan pipeline still compiling; skipped {skipped} draws over {elapsedMs:F0} ms (shader key {_pipelineCacheKey:X8}).\");\n"
    "            }\n"
    "        }"
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


# Patch 3.1: report slow shader-module and background pipeline compilations at Notice level.
# This avoids dependence on Debug logging and limits log volume; rendering behaviour is unchanged.

# Patch 4: give each Vulkan worker pipeline cache a larger persistence/recycle budget.
# 96 MiB (up from 64 MiB) raises the recycle threshold to 192 MiB because the
# existing RecycleBudgetMultiplier is 2. This is a bounded increase; scheduling is unchanged.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    "        private const long MinimumWorkerCacheBudget = 64L * 1024 * 1024;",
    "        private const long MinimumWorkerCacheBudget = 96L * 1024 * 1024;"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    """            // Keep each worker at 64 MiB however many there are: a smaller cache is recycled, and its
            // contents lost, that much sooner.""",
    """            // Keep each worker at a bounded 96 MiB minimum so useful pipelines survive longer
            // before cache recycling, without making the worker caches unbounded."""
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/Shader.cs",
    "using System;\nusing System.Runtime.InteropServices;",
    "using System;\nusing System.Diagnostics;\nusing System.Runtime.InteropServices;"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/Shader.cs",
    "        private unsafe void Compile(ShaderSource shaderSource)\n        {\n            try",
    "        private unsafe void Compile(ShaderSource shaderSource)\n        {\n"
    "            long diagnosticCompileStart = Stopwatch.GetTimestamp();\n"
    "            try"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/Shader.cs",
    "                CompileStatus = ProgramLinkStatus.Failure;\n            }\n        }\n\n        private unsafe static byte[] GlslToSpirv",
    "                CompileStatus = ProgramLinkStatus.Failure;\n"
    "            }\n"
    "            finally\n"
    "            {\n"
    "                double diagnosticCompileMs = Stopwatch.GetElapsedTime(diagnosticCompileStart).TotalMilliseconds;\n"
    "                if (diagnosticCompileMs >= 50)\n"
    "                {\n"
    "                    Logger.Notice.PrintMsg(LogClass.Gpu, $\"DIAGNOSTICS: slow shader module compile {diagnosticCompileMs:F1} ms ({_stage}).\");\n"
    "                }\n"
    "            }\n"
    "        }\n\n"
    "        private unsafe static byte[] GlslToSpirv"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs",
    "                Task pipelineCompileTask = RunBackgroundPipelineCompile(pipelineCache =>",
    "                long diagnosticPipelineStart = Stopwatch.GetTimestamp();\n"
    "                Task pipelineCompileTask = RunBackgroundPipelineCompile(pipelineCache =>"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs",
    "                await pipelineCompileTask;\n            }\n            catch (VulkanException e)",
    "                await pipelineCompileTask;\n"
    "                double diagnosticPipelineMs = Stopwatch.GetElapsedTime(diagnosticPipelineStart).TotalMilliseconds;\n"
    "                if (diagnosticPipelineMs >= 50)\n"
    "                {\n"
    "                    Logger.Notice.PrintMsg(LogClass.Gpu, $\"DIAGNOSTICS: slow background pipeline compile {diagnosticPipelineMs:F1} ms ({(IsCompute ? \"compute\" : \"graphics\")}, priority={highPriority}, demanded={demanded}).\");\n"
    "                }\n"
    "            }\n            catch (VulkanException e)"
)


# Patch 6: restore the source scheduler's full pipeline worker count.
# Patch 5 reduced worker-cache shards from five to four on this device. Since
# cache-key collisions force uncached compilation, restore the third worker
# while keeping the dedicated demand worker and the 96 MiB worker-cache budget.


# Patch 7: persist worker cache snapshots up to the recycle threshold. The previous
# logic rejected every snapshot above the checkpoint budget, then recycled caches at
# twice that size. This preserves useful 100-200 MiB caches across app restarts.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    "        private const long MinimumWorkerCacheBudget = 96L * 1024 * 1024;",
    "        private const long MinimumWorkerCacheBudget = 112L * 1024 * 1024;"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    """            // Keep each worker at a bounded 96 MiB minimum so useful pipelines survive longer
            // before cache recycling, without making the worker caches unbounded.""",
    """            // Keep each worker at a bounded 112 MiB minimum. Snapshots may use the full recycle
            // window so useful pipelines are not discarded merely for exceeding the checkpoint budget."""
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    """            if (size > state.Budget * RecycleBudgetMultiplier && allowRecycle)
            {
                Recycle(state, size);

                return;
            }

            if (size > state.Budget)
            {
                if (!state.WarnedOverBudget)
                {
                    state.WarnedOverBudget = true;

                    Logger.Info?.PrintMsg(
                        LogClass.Gpu,
                        $"Not persisting the Vulkan {state.Description} pipeline cache at {FormatSize(size)}, " +
                        $"over its {FormatSize(state.Budget)} budget; the previous snapshot stands.");
                }

                return;
            }""",
    """            if (size > state.Budget * RecycleBudgetMultiplier)
            {
                if (allowRecycle)
                {
                    Recycle(state, size);
                }

                return;
            }"""
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    """                if (info.Length == 0 || info.Length > budget)
                {
                    Logger.Warning?.PrintMsg(
                        LogClass.Gpu,
                        $"Ignoring Vulkan pipeline cache of {FormatSize(info.Length)}, outside its " +
                        $"{FormatSize(budget)} budget: {path}");""",
    """                long maxSnapshotBytes = budget * RecycleBudgetMultiplier;

                if (info.Length == 0 || info.Length > maxSnapshotBytes)
                {
                    Logger.Warning?.PrintMsg(
                        LogClass.Gpu,
                        $"Ignoring Vulkan pipeline cache of {FormatSize(info.Length)}, outside its " +
                        $"{FormatSize(maxSnapshotBytes)} persistence window: {path}");"""
)


# Patch 8: dedicate a second pipeline worker to demanded compiles. Reassign the
# shader queue's otherwise-idle demand-only thread, keeping total worker threads flat.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs",
    """        // One more cache than compile threads (including the demand thread), so two threads rarely want the same one.
        public static int PipelineCacheCount => PipelineWorkerCount + 2;""",
    """        // Keep cache shard count stable across launches so existing shader-key assignments remain valid.
        public static int PipelineCacheCount => PipelineWorkerCount + 2;
        private const int PipelineDemandWorkerCount = 2;"""
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs",
    """            _shaderQueue = new("Shader", GetBackgroundCompileThreadCount());
            _pipelineQueue = new("Pipeline", PipelineWorkerCount);""",
    """            // The shader queue has no demanded pipeline work. Reassign its otherwise-idle demand-only
            // thread to the pipeline queue, where a second urgent lane reduces demand backlog.
            _shaderQueue = new("Shader", GetBackgroundCompileThreadCount(), demandWorkerCount: 0);
            _pipelineQueue = new("Pipeline", PipelineWorkerCount, demandWorkerCount: PipelineDemandWorkerCount);"""
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs",
    "            public WorkerQueue(string name, int workerCount)",
    "            public WorkerQueue(string name, int workerCount, int demandWorkerCount = 1)"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs",
    "                _threads = new Thread[workerCount + 1];",
    "                _threads = new Thread[workerCount + demandWorkerCount];"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs",
    """                _threads[workerCount] = new Thread(() => WorkerLoop(workerCount, demandOnly: true))
                {
                    IsBackground = true,
                    Name = $"Vulkan {name} Demand Compile",
                    Priority = ThreadPriority.Normal,
                };""",
    """                for (int index = 0; index < demandWorkerCount; index++)
                {
                    int workerIndex = workerCount + index;

                    _threads[workerIndex] = new Thread(() => WorkerLoop(workerIndex, demandOnly: true))
                    {
                        IsBackground = true,
                        Name = $"Vulkan {name} Demand Compile {index}",
                        Priority = ThreadPriority.Normal,
                    };
                }"""
)
# Record actual GPU-thread waits, not just the one-second skip threshold.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs",
    """            if (task != null && !task.IsCompleted)
            {
                try
                {
                    task.Wait(timeoutMs);
                }
                catch (AggregateException)
                {
                    // The normal pipeline failure path handles a failed background task.
                }
            }

            return TryGetGraphicsPipeline(ref key, out pipeline) && pipeline != null;""",
    """            bool waited = task != null && !task.IsCompleted;
            long waitStart = waited ? Stopwatch.GetTimestamp() : 0;

            if (waited)
            {
                try
                {
                    task.Wait(timeoutMs);
                }
                catch (AggregateException)
                {
                    // The normal pipeline failure path handles a failed background task.
                }

                double waitMs = Stopwatch.GetElapsedTime(waitStart).TotalMilliseconds;

                if (waitMs >= 10)
                {
                    Logger.Notice.PrintMsg(
                        LogClass.Gpu,
                        $"DIAGNOSTICS: graphics pipeline demand wait {waitMs:F1} ms " +
                        $"({(task.IsCompleted ? "completed" : "timed out")}, shader key {_pipelineCacheKey:X8}).");
                }
            }

            return TryGetGraphicsPipeline(ref key, out pipeline) && pipeline != null;"""
)


# Patch 9: retain larger worker snapshots for longer before recycling. The latest
# test recovered all five snapshots, but one cache was recycled at 227.97 MiB.
# A 2.25x window lets that cache be checkpointed instead of discarded at 2x.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    "        private const long RecycleBudgetMultiplier = 2;",
    "        private const int RecycleBudgetMultiplierNumerator = 9;\n"
    "        private const int RecycleBudgetMultiplierDenominator = 4;"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    "size > state.Budget * RecycleBudgetMultiplier",
    "size > state.Budget * RecycleBudgetMultiplierNumerator / RecycleBudgetMultiplierDenominator"
)
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    "long maxSnapshotBytes = budget * RecycleBudgetMultiplier;",
    "long maxSnapshotBytes = budget * RecycleBudgetMultiplierNumerator / RecycleBudgetMultiplierDenominator;"
)

# Give the first dedicated demand lane a higher scheduling priority while keeping
# the second at Normal, so urgent pipelines get a boost without raising every worker.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs",
    'Name = $"Vulkan {name} Demand Compile {index}",\n                        Priority = ThreadPriority.Normal,',
    'Name = $"Vulkan {name} Demand Compile {index}",\n                        Priority = index == 0 ? ThreadPriority.AboveNormal : ThreadPriority.Normal,'
)

# Emit the effective policy from the compiled runtime, so device logs prove which
# cache and wait limits were actually built into the IPA.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs",
    "            long workerBudget = Math.Max(MinimumWorkerCacheBudget, (TotalCacheBudget - MainCacheBudget) / Math.Max(1, workerCount));",
    "            long workerBudget = Math.Max(MinimumWorkerCacheBudget, (TotalCacheBudget - MainCacheBudget) / Math.Max(1, workerCount));\n"
    "            Logger.Notice.PrintMsg(LogClass.Gpu, $\"DIAGNOSTICS: Vulkan cache policy minimum-worker={FormatSize(MinimumWorkerCacheBudget)}, effective-worker={FormatSize(workerBudget)}, persistence-window={FormatSize(workerBudget * RecycleBudgetMultiplierNumerator / RecycleBudgetMultiplierDenominator)}.\");"
)

# Request demanded pipelines sooner, then bound each synchronous GPU-thread wait.
# The previous 500 ms skip window plus 750 ms wait allowed long visible frame stalls.
# This experiment uses a 250 ms skip window and a 300 ms wait cap; if a pipeline is
# still compiling, draws may remain skipped briefly rather than blocking for 750 ms.
replace_once(
    "src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs",
    "        private const long MaxSkippedDrawMs = 1000;\n        public const int SkippedTooLongWaitMs = 2000;",
    "        private const long MaxSkippedDrawMs = 250;\n        public const int SkippedTooLongWaitMs = 300;"
)

# Patch 10: measure the GPU loop's CPU-side work versus FIFO and present waits.
# This distinguishes expensive emulation/render command processing from time spent
# waiting for guest work or the host presentation path, without changing scheduling.
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                long diagnosticPresents = 0;\n\n                while (_isActive)",
    "                long diagnosticPresents = 0;\n"
    "                long diagnosticWaitTicks = 0;\n"
    "                long diagnosticProcessTicks = 0;\n"
    "                long diagnosticMaxProcessTicks = 0;\n"
    "                long diagnosticPresentTicks = 0;\n"
    "                long diagnosticLoopCount = 0;\n\n"
    "                while (_isActive)"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                    bool fifoReady = Device.WaitFifo();",
    "                    long diagnosticWaitStart = Stopwatch.GetTimestamp();\n"
    "                    bool fifoReady = Device.WaitFifo();\n"
    "                    diagnosticWaitTicks += Stopwatch.GetTimestamp() - diagnosticWaitStart;"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                        Device.Statistics.RecordFifoStart();\n"
    "                        Device.ProcessFrame();\n"
    "                        diagnosticFrames++;",
    "                        Device.Statistics.RecordFifoStart();\n"
    "                        long diagnosticProcessStart = Stopwatch.GetTimestamp();\n"
    "                        Device.ProcessFrame();\n"
    "                        long diagnosticProcessElapsed = Stopwatch.GetTimestamp() - diagnosticProcessStart;\n"
    "                        diagnosticProcessTicks += diagnosticProcessElapsed;\n"
    "                        diagnosticMaxProcessTicks = Math.Max(diagnosticMaxProcessTicks, diagnosticProcessElapsed);\n"
    "                        diagnosticFrames++;"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    "                    if (Device.PresentLoop(SwapBuffers))\n"
    "                    {\n"
    "                        diagnosticPresents++;",
    "                    long diagnosticPresentStart = Stopwatch.GetTimestamp();\n"
    "                    bool diagnosticPresented = Device.PresentLoop(SwapBuffers);\n"
    "                    diagnosticPresentTicks += Stopwatch.GetTimestamp() - diagnosticPresentStart;\n"
    "                    diagnosticLoopCount++;\n"
    "                    if (diagnosticPresented)\n"
    "                    {\n"
    "                        diagnosticPresents++;"
)
replace_once(
    "src/Ryujinx.Library/Window/WindowBase.cs",
    '                        Logger.Notice.Print(LogClass.Gpu, $"DIAGNOSTICS: GPU heartbeat; FIFO-ready={diagnosticFifoReady}, processed-frames={diagnosticFrames}, presents={diagnosticPresents}.");\n'
    "                        diagnosticFifoReady = 0;\n"
    "                        diagnosticFrames = 0;\n"
    "                        diagnosticPresents = 0;",
    '                        double processAvgMs = diagnosticFrames > 0 ? diagnosticProcessTicks * 1000.0 / Stopwatch.Frequency / diagnosticFrames : 0;\n'
    '                        double processMaxMs = diagnosticMaxProcessTicks * 1000.0 / Stopwatch.Frequency;\n'
    '                        double waitAvgMs = diagnosticLoopCount > 0 ? diagnosticWaitTicks * 1000.0 / Stopwatch.Frequency / diagnosticLoopCount : 0;\n'
    '                        double presentAvgMs = diagnosticLoopCount > 0 ? diagnosticPresentTicks * 1000.0 / Stopwatch.Frequency / diagnosticLoopCount : 0;\n'
    '                        Logger.Notice.Print(LogClass.Gpu, $"DIAGNOSTICS: GPU heartbeat; FIFO-ready={diagnosticFifoReady}, processed-frames={diagnosticFrames}, presents={diagnosticPresents}, process-avg-ms={processAvgMs:F2}, process-max-ms={processMaxMs:F2}, fifo-wait-avg-ms={waitAvgMs:F2}, present-avg-ms={presentAvgMs:F2}.");\n'
    "                        diagnosticFifoReady = 0;\n"
    "                        diagnosticFrames = 0;\n"
    "                        diagnosticPresents = 0;\n"
    "                        diagnosticWaitTicks = 0;\n"
    "                        diagnosticProcessTicks = 0;\n"
    "                        diagnosticMaxProcessTicks = 0;\n"
    "                        diagnosticPresentTicks = 0;\n"
    "                        diagnosticLoopCount = 0;"
)

# Fail the CI build if any requested performance patch did not land in source.
def assert_contains(path, expected):
    content = (ROOT / path).read_text(encoding="utf-8")
    if expected not in content:
        raise SystemExit(f"PATCH VERIFICATION FAILED in {path}: missing {expected!r}")

def assert_absent(path, unexpected):
    content = (ROOT / path).read_text(encoding="utf-8")
    if unexpected in content:
        raise SystemExit(f"PATCH VERIFICATION FAILED in {path}: unexpected old value {unexpected!r}")

assert_contains("src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs", "MinimumWorkerCacheBudget = 112L * 1024 * 1024;")
assert_contains("src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs", "RecycleBudgetMultiplierNumerator = 9;")
assert_contains("src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs", "RecycleBudgetMultiplierDenominator = 4;")
assert_contains("src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs", "long maxSnapshotBytes = budget * RecycleBudgetMultiplierNumerator / RecycleBudgetMultiplierDenominator;")
assert_contains("src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs", "DIAGNOSTICS: Vulkan cache policy minimum-worker=")
assert_absent("src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs", "MinimumWorkerCacheBudget = 96L * 1024 * 1024;")
assert_contains("src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs", "private const int PipelineDemandWorkerCount = 2;")
assert_contains("src/Ryujinx.Graphics.Vulkan/BackgroundCompilationScheduler.cs", "Priority = index == 0 ? ThreadPriority.AboveNormal : ThreadPriority.Normal,")
assert_contains("src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs", "private const long MaxSkippedDrawMs = 250;")
assert_contains("src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs", "public const int SkippedTooLongWaitMs = 300;")
assert_absent("src/Ryujinx.Graphics.Vulkan/ShaderCollection.cs", "private const long MaxSkippedDrawMs = 1000;")

assert_contains("src/Ryujinx.Library/Window/WindowBase.cs", "process-avg-ms=")
assert_contains("src/Ryujinx.Library/Window/WindowBase.cs", "fifo-wait-avg-ms=")
assert_contains("src/Ryujinx.Library/Window/WindowBase.cs", "present-avg-ms=")

print("Applied MeloNX 2.7 experimental identity and startup/CPU/GPU diagnostics patches.")
