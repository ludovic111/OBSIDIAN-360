Your objective is to reverse-engineer this Xbox 360 as deeply and completely as possible and document everything inside this repository.

Treat the console as an open-ended hardware and software research project. You have broad freedom to inspect, analyze, test, redesign, rewrite, replace, optimize, modernize, and document any part of the system that can realistically be accessed.

This is not merely a preservation project. One of the central goals is to determine how far the Xbox 360 can be transformed into a modern, optimized, understandable, maintainable computing platform while preserving useful compatibility with its original hardware and legitimate Xbox 360 software.

Main objectives:

1. Reverse-engineer the Xbox 360 hardware and software architecture as completely as possible:
   - CPU architecture and boot process
   - GPU and graphics pipeline
   - RAM architecture and memory mapping
   - NAND / flash storage
   - Southbridge, buses, controllers, peripherals, USB, Ethernet, SATA, AV/HDMI, etc.
   - DVD drive, its firmware, communication protocol, authentication mechanisms, and failure modes
   - Boot ROM / bootloaders / hypervisor / kernel / dashboard architecture
   - Device initialization
   - Power management
   - Thermal management
   - Security architecture
   - Hardware revisions and anything specific to this particular console
2. Document EVERYTHING you discover.

   The repository should progressively become a complete technical knowledge base for this exact console.

   Record:
   - hardware identification
   - chip markings
   - memory maps
   - registers
   - protocols
   - boot sequences
   - firmware formats
   - filesystem structures
   - executable formats
   - graphics formats
   - audio formats
   - experiments
   - successful and failed attempts
   - hypotheses
   - measurements
   - logs
   - dumps
   - scripts
   - tools
   - source code
   - build instructions
   - diagrams
   - troubleshooting notes
   - references
   - limitations
   - unanswered questions
   - anything else that may be useful
   Do not discard failed experiments. Document why they failed and what was learned.
3. Reverse-engineer how Xbox 360 games work from every technically accessible angle.

   I want a deep understanding of the complete lifecycle of an Xbox 360 game, from inserting a legitimate game disc to executing gameplay.

   Investigate and document areas such as:
   - physical disc structure
   - filesystem layout
   - executable formats
   - game packaging
   - executable loading
   - memory layout
   - CPU code
   - PowerPC instruction usage
   - GPU command generation
   - shaders
   - textures
   - models
   - animation formats
   - audio
   - video
   - input
   - networking
   - save data
   - achievements
   - Xbox system APIs
   - kernel calls
   - runtime libraries
   - middleware
   - threading
   - synchronization
   - memory allocation
   - streaming systems
   - asset loading
   - game initialization
   - frame lifecycle
   - rendering pipeline
   - filesystem access
   - error handling
   - performance characteristics
   Where technically and legally possible, examine legitimately owned Xbox 360 games at the lowest practical level.

   If the DVD drive is repaired and legitimate Xbox 360 discs can be read, create tooling to inspect the software on those discs as deeply as possible.

   Analyze binaries through techniques such as:
   - static analysis
   - disassembly
   - decompilation
   - symbol reconstruction
   - control-flow analysis
   - call-graph generation
   - binary diffing
   - runtime tracing
   - memory inspection
   - profiling
   - API tracing
   - file-format analysis
   The goal is to understand what the game is doing down to individual machine instructions where feasible, reconstruct higher-level program structure when possible, and document how Xbox 360 software interacts with the console.

   Build reusable research tools rather than performing one-off manual analysis whenever possible.

   Do not publish copyrighted game assets, proprietary game binaries, cryptographic secrets, authentication keys, or other material that should not be redistributed. Documentation, original tooling, independently written code, metadata, hashes, structural descriptions, and research findings should be preferred.
4. Investigate whether the console can boot directly into Linux with a usable graphical desktop.

   The ideal final experience is:

   Power button → boot process → Linux → graphical desktop

   with as little dependency as possible on the original Xbox dashboard.

   Explore every realistic route for achieving this, including custom bootloaders, modified firmware, alternative kernels, Linux ports, hardware exploits, chainloading, or replacement components.
5. Optimize Linux specifically for the Xbox 360 hardware.

   Do not treat this as a generic Linux installation. Build or configure the system around the exact limitations and strengths of the console.

   Investigate:
   - custom kernel configuration
   - CPU scheduling
   - memory usage
   - GPU acceleration
   - storage performance
   - networking
   - boot time
   - thermal behavior
   - power usage
   - controller/input support
   - display output
   - lightweight desktop environments
   - modern compiler optimizations
   Where useful, modern languages such as Rust may be used for new tooling, drivers, system components, utilities, boot infrastructure, or replacement software.
6. Aggressively investigate modernization opportunities.

   Do not assume that the original Xbox 360 architecture must remain intact.

   You have permission to rethink, replace, or redesign software architecture whenever a modern approach would provide a meaningful improvement.

   Think of the original console as hardware that happens to come with a legacy software stack, rather than treating that legacy stack as immutable.

   Investigate whether old components can be replaced with:
   - modern boot infrastructure
   - modern operating-system components
   - modern drivers
   - safer languages
   - Rust components
   - modern memory-safety techniques
   - modern debugging infrastructure
   - modern observability
   - structured logging
   - better crash reporting
   - improved scheduling
   - better resource management
   - modern filesystems where appropriate
   - modern networking stacks
   - better caching
   - asynchronous I/O
   - optimized graphics paths
   - optimized audio paths
   - modern build systems
   - reproducible builds
   - automated testing
   - fuzzing
   - emulation-assisted testing
   - continuous integration
   If an existing component is unnecessarily complex, inefficient, opaque, fragile, or outdated, investigate replacing it.

   You may redesign large portions of the software stack if justified.

   This can extend all the way from user-space applications to drivers, kernels, bootloaders, firmware-like components, hardware abstraction layers, and other low-level software where technically possible.

   Rust, C, C++, assembly, or another appropriate language may be used.

   Do not use Rust merely for the sake of using Rust. Use the language that best fits each layer, but strongly consider modern memory-safe implementations for newly written components where performance permits.

   Measure improvements wherever possible.

   Compare:
   - original behavior
   - modified behavior
   - performance
   - memory consumption
   - latency
   - boot time
   - stability
   - temperatures
   - maintainability
7. Investigate and attempt to repair the DVD drive.

   Diagnose the hardware and software side of the drive as completely as possible.

   Investigate:
   - electronics
   - mechanical components
   - laser behavior
   - spindle behavior
   - tray mechanism
   - SATA communication
   - firmware behavior
   - drive identification
   - error codes
   - communication with the Xbox motherboard
   If realistically possible, restore normal reading functionality.

   If the drive becomes functional, the target is for the console to once again read my legitimate Xbox 360 game discs.

   Once reading works, use those discs as another source of technical understanding of the platform and game architecture, within applicable legal limits.

   Preserve compatibility with legitimate Xbox 360 discs where possible.
8. Reimplement components where doing so provides a technical advantage.

   You are not limited to patching the existing software.

   If useful, design or implement replacements for:
   - bootloaders
   - drivers
   - firmware components
   - hardware abstraction layers
   - system utilities
   - debugging tools
   - diagnostic software
   - monitoring systems
   - Linux integration layers
   - game-analysis tools
   - executable parsers
   - Xbox-specific developer tools
   Prefer correctness, observability, stability, performance, reproducibility, and maintainability over blindly preserving legacy architecture.
9. Build tooling around the research.

   Create scripts and programs whenever they make the investigation more reproducible.

   Examples:
   - hardware probing tools
   - serial/debug logging tools
   - NAND parsers
   - firmware analysis tools
   - binary parsers
   - executable analyzers
   - disassemblers or integrations with existing disassemblers
   - control-flow visualization tools
   - register explorers
   - memory dump analyzers
   - filesystem inspection tools
   - disc inspection tools
   - shader extraction/analysis tools
   - boot image builders
   - diagnostic utilities
   - automated documentation generators
   - benchmarking tools
   - fuzzing harnesses
   - hardware test suites
10. Make the work reproducible.

Someone cloning this repository should eventually be able to understand:

- what console/revision was analyzed
- how every discovery was made
- how to reproduce experiments
- how to build every custom component
- how to install the resulting system
- how to recover the console if something fails
- what remains unknown

11. Protect recoverability.

Before performing destructive modifications, obtain and preserve all recoverable original data such as firmware, NAND contents, configuration information, drive data, and relevant identifiers.

Prefer reversible experiments first.

Clearly document brick risks and recovery procedures before attempting dangerous modifications.

Never destroy the only known copy of original console data.

12. Operate autonomously.

I am going to sleep after starting this task and will not be available to interact with the console, answer questions, connect cables, press buttons, reboot hardware manually, move devices, or perform physical actions until tomorrow morning.

Therefore, continue working autonomously for as long as productive work remains that does not require physical intervention from me.

Do not stop merely because a question could be asked.

When information is uncertain:

- investigate it
- inspect existing data
- inspect the repository
- consult available documentation and source material
- form hypotheses
- test them where safely possible
- document assumptions

If one research path becomes blocked because physical interaction is required, document exactly what is required and immediately continue with another independent task.

Maintain a TODO / BLOCKED list containing anything that will require my intervention tomorrow.

While unattended, prioritize work that cannot physically damage or irreversibly brick the console.

Do not perform irreversible operations without an established recovery path.

Continue improving documentation, tooling, architecture, analysis, code, tests, and research rather than waiting for me.

13. Maintain a detailed research journal.

Keep an ongoing chronological log containing:

- timestamp
- objective
- action
- observation
- result
- interpretation
- next step

This should make it possible to reconstruct the entire investigation afterward.

14. Publish the project on GitHub.

You may create and maintain a public GitHub repository for this project.

Organize it as a serious open-source reverse-engineering and systems-research project.

Include:

- README
- project goals
- current status
- hardware information
- architecture documentation
- build instructions
- installation instructions
- experiment logs
- diagrams
- research notes
- source code
- issue/task tracking
- contribution guidelines where useful
- licenses for original code where appropriate

Commit regularly with descriptive commit messages so that the development history itself documents the progression of the project.

However, before every public commit or push, ensure that the repository does NOT contain:

- private keys
- cryptographic secrets
- console-specific secret keys
- credentials
- authentication tokens
- personally identifying data
- proprietary firmware dumps that cannot legally be redistributed
- copyrighted Xbox game executables
- copyrighted game assets
- complete disc images
- other confidential or non-redistributable material

Such material may be referenced by hashes, filenames, offsets, metadata, structural documentation, or local-only paths when useful, but must remain outside the public repository.

Repository philosophy:

This repository should become an exhaustive technical record of the project rather than merely a collection of working code.

Document continuously while you work.

Create a clean structure such as:

/docs\
/hardware\
/firmware\
/boot\
/linux\
/kernel\
/drivers\
/dvd\
/games\
/game-analysis\
/tools\
/experiments\
/dumps-local\
/logs\
/benchmarks\
/tests\
/diagrams\
/src

Keep sensitive or non-redistributable dumps outside Git tracking.

The long-term goal is to understand this Xbox 360 from the lowest accessible hardware level to the highest software level, understand exactly how Xbox 360 games execute on it, make the hardware as useful as realistically possible with modern software, and leave behind enough documentation that another engineer could continue the project without needing any undocumented knowledge.

Do not stop at the first working solution.

Once something works:

1. understand why it works;
2. document it;
3. test it;
4. benchmark it;
5. inspect what happens internally;
6. identify bottlenecks;
7. modernize it where useful;
8. optimize it;
9. make it reproducible;
10. determine what can be improved next.

The objective is not merely to make the Xbox 360 work.

The objective is to understand it, modernize it, optimize it, extend it, and document it as completely as realistically possible.