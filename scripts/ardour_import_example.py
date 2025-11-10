#!/usr/bin/env python3
"""
Ardour Import Example
=====================

Demonstrates how to import audio files into Ardour using ardour-mcp tools.

This script shows the MCP commands you would use through Claude or directly
via the MCP protocol to import MIDI-rendered audio into an Ardour session.

Note: This is a documentation/example script showing the workflow.
For actual usage, use Claude with ardour-mcp configured, or call the MCP
tools directly through the MCP protocol.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class ArdourImportWorkflow:
    """
    Example workflow for importing audio into Ardour via MCP.

    This class demonstrates the sequence of MCP tool calls needed to:
    1. Create tracks in Ardour
    2. Import audio files to tracks
    3. Set up basic mixing
    4. Configure monitoring and routing
    """

    def __init__(self):
        self.commands = []

    def add_command(self, tool: str, arguments: Dict[str, Any], description: str):
        """Add a command to the workflow."""
        self.commands.append({
            "tool": tool,
            "arguments": arguments,
            "description": description
        })

    def create_track_workflow(self, audio_files: List[Path]) -> None:
        """
        Create a workflow for importing multiple audio files.

        Args:
            audio_files: List of audio file paths to import
        """
        print("\n" + "=" * 70)
        print("Ardour Import Workflow via MCP")
        print("=" * 70)

        # Step 1: Get session info
        self.add_command(
            tool="get_session_info",
            arguments={},
            description="Get current Ardour session information"
        )

        # Step 2: Create tracks for each audio file
        for audio_file in audio_files:
            track_name = audio_file.stem.replace('_', ' ').title()

            self.add_command(
                tool="create_audio_track",
                arguments={
                    "name": track_name,
                    "channels": 2  # Stereo
                },
                description=f"Create stereo audio track '{track_name}'"
            )

        # Step 3: Document audio import process
        print("\n\nWorkflow Steps:")
        print("-" * 70)

        for i, cmd in enumerate(self.commands, 1):
            print(f"\n{i}. {cmd['description']}")
            print(f"   Tool: {cmd['tool']}")
            print(f"   Arguments: {json.dumps(cmd['arguments'], indent=6)}")

        # Step 4: Show manual import instructions
        print("\n\nManual Audio Import:")
        print("-" * 70)
        print("After creating tracks, import audio manually in Ardour:")
        print("\n1. In Ardour, select Region > Import")
        print("2. Navigate to the audio files:")
        for audio_file in audio_files:
            print(f"   - {audio_file}")
        print("3. Drag files to corresponding tracks")
        print("4. Or use 'Add files as new tracks' option")

        # Step 5: Show post-import mixing workflow
        print("\n\nPost-Import Mixing Workflow (via MCP):")
        print("-" * 70)

        mixing_workflow = [
            {
                "description": "Set all tracks to unity gain (0dB)",
                "tool": "set_track_gain_batch",
                "arguments": {
                    "track_ids": [1, 2, 3],
                    "gain_db": 0.0
                }
            },
            {
                "description": "Pan bass track to center, others slightly wide",
                "tool": "set_track_pan",
                "arguments": {
                    "track_id": 1,
                    "pan_position": 0.0  # Center (-1.0 = left, 1.0 = right)
                }
            },
            {
                "description": "Enable input monitoring on all tracks",
                "tool": "set_track_monitor_input",
                "arguments": {
                    "track_id": 1,
                    "enabled": True
                }
            },
            {
                "description": "Create a master bus for submix",
                "tool": "create_audio_track",
                "arguments": {
                    "name": "Submix Bus",
                    "channels": 2
                }
            },
        ]

        for i, step in enumerate(mixing_workflow, 1):
            print(f"\n{i}. {step['description']}")
            print(f"   Tool: {step['tool']}")
            print(f"   Arguments: {json.dumps(step['arguments'], indent=6)}")

    def print_claude_examples(self, audio_files: List[Path]) -> None:
        """Print example Claude prompts for the import workflow."""

        print("\n\n" + "=" * 70)
        print("Claude Prompt Examples (Natural Language)")
        print("=" * 70)

        print("\n\nExample 1: Quick Import Setup")
        print("-" * 70)
        print("Prompt to Claude:")
        print('"""')
        print("I have three audio files rendered from MIDI that I want to import")
        print("into Ardour. Create three stereo tracks called:")
        for audio_file in audio_files:
            track_name = audio_file.stem.replace('_', ' ').title()
            print(f"  - {track_name}")
        print("\nSet them all to 0dB gain, enable input monitoring, and make sure")
        print("they're all ready for mixing.")
        print('"""')

        print("\n\nExample 2: Import with Mixing Setup")
        print("-" * 70)
        print("Prompt to Claude:")
        print('"""')
        print("I need to set up a mixing session for drum, bass, and melody tracks.")
        print("Create the three tracks, then:")
        print("  1. Pan the drum track 10% left for width")
        print("  2. Pan the melody 10% right to balance")
        print("  3. Keep bass centered")
        print("  4. Set bass to -3dB to leave headroom")
        print("  5. Create a 'Mix Bus' track for parallel processing")
        print("  6. Route all three tracks to the mix bus at -6dB")
        print('"""')

        print("\n\nExample 3: Advanced Automation Setup")
        print("-" * 70)
        print("Prompt to Claude:")
        print('"""')
        print("For my three imported tracks (bass, drums, melody):")
        print("  1. Set up gain automation in TOUCH mode on the melody track")
        print("  2. Set up pan automation in WRITE mode on the drums")
        print("  3. Create markers at bars 1, 5, 9, and 13 labeled")
        print("     'Intro', 'Verse', 'Chorus', and 'Outro'")
        print("  4. Set up a loop from bar 5 to bar 9 for the verse section")
        print('"""')

    def generate_python_mcp_example(self, audio_files: List[Path]) -> None:
        """Generate example Python code for direct MCP usage."""

        print("\n\n" + "=" * 70)
        print("Direct MCP Protocol Usage (Python)")
        print("=" * 70)

        print("""
This example shows how to interact with ardour-mcp directly via the
Model Context Protocol, without using Claude as an intermediary.

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def import_audio_to_ardour():
    \"\"\"Import audio files to Ardour using MCP tools directly.\"\"\"

    # Connect to ardour-mcp server
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            "/home/beengud/raibid-labs/ardour-mcp",
            "run",
            "ardour-mcp"
        ]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get session info
            result = await session.call_tool(
                "get_session_info",
                arguments={}
            )
            print(f"Session: {result}")
""")

        # Generate track creation code
        print("            # Create tracks for each audio file")
        for audio_file in audio_files:
            track_name = audio_file.stem.replace('_', ' ').title()
            print(f"""
            result = await session.call_tool(
                "create_audio_track",
                arguments={{
                    "name": "{track_name}",
                    "channels": 2
                }}
            )
            print(f"Created track: {{result}}")""")

        print("""
            # Set up mixing
            await session.call_tool(
                "set_track_gain_batch",
                arguments={
                    "track_ids": [1, 2, 3],
                    "gain_db": 0.0
                }
            )

            # Enable monitoring
            for track_id in [1, 2, 3]:
                await session.call_tool(
                    "set_track_monitor_input",
                    arguments={
                        "track_id": track_id,
                        "enabled": True
                    }
                )

            print("Import workflow complete!")

# Run the workflow
asyncio.run(import_audio_to_ardour())
```
""")


def demonstrate_ardour_import():
    """Demonstrate the complete Ardour import workflow."""

    # Example audio files (from MIDI rendering pipeline)
    audio_files = [
        Path("/tmp/midi_test/808_bass.wav"),
        Path("/tmp/midi_test/drum_beat.wav"),
        Path("/tmp/midi_test/melody.wav"),
    ]

    print("=" * 70)
    print("MIDI to Ardour Import Workflow")
    print("=" * 70)
    print("\nThis demonstrates importing MIDI-rendered audio into Ardour")
    print("using the ardour-mcp Model Context Protocol server.")

    workflow = ArdourImportWorkflow()

    # Show the workflow
    workflow.create_track_workflow(audio_files)

    # Show Claude examples
    workflow.print_claude_examples(audio_files)

    # Show Python MCP example
    workflow.generate_python_mcp_example(audio_files)

    # Final summary
    print("\n\n" + "=" * 70)
    print("Integration Summary")
    print("=" * 70)
    print("""
The complete pipeline:

1. Generate MIDI programmatically (midiutil)
   → Create drum patterns, bass lines, melodies in Python

2. Render MIDI to audio (FluidSynth)
   → Convert MIDI to high-quality WAV files using soundfonts

3. Import to Ardour (ardour-mcp + Claude)
   → Use natural language to create tracks, import audio, set up mixing

4. Mix and master (ardour-mcp tools)
   → Control gain, pan, routing, automation via MCP

This workflow enables AI-assisted music production where:
- MIDI is generated by AI or algorithms
- FluidSynth renders realistic audio
- Claude controls Ardour for professional mixing
- All steps are scriptable and automatable

For live usage:
- Use the midi_to_audio_pipeline.py script to generate and render
- Use Claude with ardour-mcp to control Ardour
- Combine AI composition, rendering, and mixing in one workflow
""")


if __name__ == "__main__":
    demonstrate_ardour_import()
