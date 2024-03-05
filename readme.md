# Cadmium Documentation

Cadmium is a comprehensive library designed to facilitate the modeling of 3-axis CNC milling processes. It provides an extensive data model encompassing tools, stock material, CNC machines, jobs, setups, operations, and cuts, enabling precise and efficient milling operations.

This library is not a G-code generator, but rather a tool for creating a model of the milling process.
It is intended to be used in conjunction with solvers that can take this data and generate gcode.
It is also intended to be used with utility libraries to generate the cut trees for common operations.

## Data Model Overview

### Tool

In Cadmium, a tool is defined as an instrument used in the milling process, categorized into two types:

#### Cutting Tool

Attributes of a cutting tool include:

- **Shank Diameter**: The diameter of the non-cutting part of the tool.
- **Cutting Geometry**: The shape of the cutting part, which can be flat, ball, chamfer, etc.
- **Cutting Diameter**: The diameter of the cutting edge.
- **Cutting Length**: The length of the cutting edge.

#### Probe Tool

Attributes of a probe tool include:

- **Shank Diameter**: The diameter of the non-probing part of the tool.
- **Probe Diameter**: The size of the probe tip, crucial for compensation calculations.
- **Probing Depth**: The maximum depth the probe can reach inside a cavity.
- **Probing Axes**: The axes along which probing can be performed.

### Stock

The stock represents the raw material from which the workpiece is crafted, characterized by:

- **Material**: The type of material, such as aluminum or steel.
- **Stock Type**: The form of the stock, for example, bar or plate.
- **Dimensions**: The size of the stock, specified by length, width, and height.

### Machine

The machine object delineates the specifications of the CNC machine, divided into:

#### Travel Properties

- **Max Spindle Speed**: The highest rotational speed of the spindle.
- **Max Feedrate**: The maximum speed at which the tool can move through the material.
- **Max Acceleration**: The greatest rate of change of the tool's speed.
- **Max Jerk**: The maximum rate of change of acceleration.

#### Physical Properties

- **Work Area**: The available space for milling operations.
- **Tool Change Procedure**: The method by which tools are exchanged.
- **Probing Stations**: Facilities for tool length and diameter measurement.

#### Machine Setup

- **Workholding**: The mechanism for securing the workpiece, such as a vise or fixture.
- **Tool Inventory**: The collection of tools available for use.
- **Current Tool in Spindle**: The tool presently mounted in the machine.
- **Workpiece Setup**: The placement and orientation of the workpiece.

### Job

A job is structured as a tree, with operations as nodes and workpiece setups as edges. This hierarchical arrangement illustrates the sequence and interdependencies of operations. Operations at the same level can be executed in any order but must follow their parent operation. The job initiates with an empty root operation, setting up the initial workpiece configuration.

### Setup

Setups are transitional phases between operations, allowing adjustments to the workpiece's positioning and orientation.

### Operation

An operation is defined by its required tool and comprises a tree of cuts, each with its own dependencies. Similar to job structure, cuts within the same branch can be conducted in any sequence but must succeed their parent cut.

### Cut

Cuts represent the actual milling operations. They are classified into two types:

- **Linear**: Straight-line cuts, corresponding to G1 G-code commands, specified by starting position and stopping position.
- **Circular**: Arc or circular cuts, associated with G2/G3 G-code commands, specified by starting position, stopping position, arc center, number of turns and direction (CW,CCW).

Each cut also has a specified feedrate and spindle speed.
    