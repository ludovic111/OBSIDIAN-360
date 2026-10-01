Your objective is to reverse-engineer this Xbox 360 as deeply and completely as possible and document everything inside this repository.

Treat the console as an open-ended hardware and software research project. You have broad freedom to inspect, analyze, test, redesign, rewrite, replace, optimize, and document any part of the system that can realistically be accessed.

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
2. Document EVERYTHING you discover.\
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
   - anything else that may be useful
   Do not discard failed experiments. Document why they failed and what was learned.
3. Investigate whether the console can boot directly into Linux with a usable graphical desktop.

   The ideal final experience is:

   Power button → boot process → Linux → graphical desktop

   with as little dependency as possible on the original Xbox dashboard.

   Explore every realistic route for achieving this, including custom bootloaders, modified firmware, alternative kernels, Linux ports, hardware exploits, chainloading, or replacement components.
4. Optimize Linux specifically for the Xbox 360 hardware.

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
5. Investigate and attempt to repair the DVD drive.

   Diagnose the hardware and software side of the drive as completely as possible.

   If realistically possible, restore normal reading functionality.

   If the drive becomes functional, investigate how the original console communicates with it and document the entire interface.

   Preserve compatibility with legitimately owned Xbox 360 discs where technically and legally possible. Do not bypass copy protection or authentication solely to enable unauthorized copies.
6. Reimplement components where doing so provides a technical advantage.

   You are not limited to patching the existing software.

   If useful, you may design or implement replacements for:
   - bootloaders
   - drivers
   - firmware components
   - hardware abstraction layers
   - system utilities
   - debugging tools
   - diagnostic software
   - monitoring systems
   - Linux integration layers
   Rust, C, C++, assembly, or any other appropriate language may be used.

   Prefer correctness, observability, stability, performance, and maintainability over blindly preserving legacy architecture.
7. Build tooling around the research.

   Create scripts and programs whenever they make the investigation more reproducible.

   Examples:
   - hardware probing tools
   - serial/debug logging tools
   - NAND parsers
   - firmware analysis tools
   - binary parsers
   - register explorers
   - memory dump analyzers
   - filesystem inspection tools
   - boot image builders
   - diagnostic utilities
   - automated documentation generators
8. Make the work reproducible.

   Someone cloning this repository should eventually be able to understand:
   - what console/revision was analyzed
   - how every discovery was made
   - how to reproduce experiments
   - how to build every custom component
   - how to install the resulting system
   - how to recover the console if something fails
   - what remains unknown
9. Protect recoverability.

   Before performing destructive modifications, obtain and preserve all recoverable original data such as firmware, NAND contents, configuration information, drive data, and relevant identifiers.

   Prefer reversible experiments first.

   Clearly document brick risks and recovery procedures before attempting dangerous modifications.

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
/tools\
/experiments\
/dumps\
/logs\
/diagrams\
/src

You have broad architectural freedom. You may restructure the repository whenever a better organization becomes obvious.

The long-term goal is to understand this Xbox 360 from the lowest accessible hardware level to the highest software level, make the hardware as useful as realistically possible with modern software, and leave behind enough documentation that another engineer could continue the project without needing any undocumented knowledge.

Do not stop at the first working solution. Once something works, understand why it works, measure it, optimize it, document it, and identify what could be improved next.