# Step 4: Create Hierarchy Diagram

## CRITICAL: Generate SVG image files, not markdown documentation

## Implementation
Write Python code to generate SVG diagram files for **each entity** from Step 3 output. The code must iterate through all entities and create a separate SVG file for each one.

Create an SVG block diagram for each entity in the hierarchical MDM data model with the following specifications:

**LAYOUT:**
- Tree structure flowing left-to-right
- Main entity box on the left with a vertical trunk line extending down
- Horizontal branch lines connecting from the trunk to each attribute/field group
- Field groups have additional connecting lines to their sub-attributes on the right
- Must fit on screen (max width: 600-1000px)

**COLOR CODING (with legend at top):**
- Business Entity: Blue (#2196F3)
- General Attributes: Light Green (#C5E1A5)
- Identifiers: Pink (#F8BBD9)
- Field Groups: Yellow/Gold (#FFD54F)

**VISUAL ELEMENTS:**
- All boxes: Rounded rectangles (rx=12)
- Box dimensions: ~145x26 pixels
- Vertical spacing: ~29px between items
- Dropdown indicator (▼ triangle) on fields with selectable values
- Connecting lines: Gray (#666), 1px stroke
- Font: Arial, 10-11px

**STRUCTURE:**
1. Title at top left (underlined)
2. Legend bar showing all color categories
3. Main entity box (blue) on left
4. Column 1: Identifiers (pink), General Attributes (green), Field Groups (yellow)
5. Column 2: Sub-attributes of field groups only (green boxes)

**DATA MODEL TO VISUALIZE:**
The code should iterate through all entities from Step 3 output and create a diagram for each. Use this format for each entity:

Entity: [ENTITY_NAME] (where ENTITY_NAME is the actual entity name from the data model)

Identifiers:
- [identifier1]
- [identifier2]

General Attributes:
- [attribute1]
- [attribute2] (dropdown)
- [attribute3]

Field Groups with Sub-attributes:
- [FieldGroup1]:
  - [sub_field1] (dropdown)
  - [sub_field2]
- [FieldGroup2]:
  - [sub_field1]
  - [sub_field2] (dropdown)

Generate a clean, professional SVG that matches this exact block diagram style.



## Output
Generate one SVG file per entity in the outputs directory. Name each file following the pattern: `step4_[entity_name]_entity_hierarchy.svg` where `[entity_name]` is the actual entity name (e.g., `step4_person_entity_hierarchy.svg`, `step4_organization_entity_hierarchy.svg`).