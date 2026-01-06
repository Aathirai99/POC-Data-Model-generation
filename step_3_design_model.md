# Step 3: Design, Build, and Document the Hierarchical Data Model

## Objective
Design and document the complete hierarchical document-style MDM data model structure based on the mappings from Step 2, following Informatica MDM SaaS best practices.

## Input
Take the mapping document output from Step 2, which includes:
- Requirements mapped to OOTB entities and fields
- Identified gaps where customization is needed
- Justifications for OOTB usage vs. custom creation decisions
- List of custom entities, custom fields, and custom attributes to be created
- Mapping matrix showing Requirement → OOTB Entity/Field → Custom Entity/Field relationships

## Tasks

### 3.1 Design Hierarchical Document-Style Structure
- Create a hierarchical structure for the data model
- Use field groups for all 1-to-many relationships
- Organize entities in a parent-child hierarchy where applicable
- Ensure the structure follows Informatica MDM native patterns

### 3.2 Implement OOTB Entities and Extensions
- Use identified OOTB entities (Person, Organization, Product) as foundation
- Add custom attributes to OOTB entities where requirements demand it
- Configure OOTB entities with their standard field groups
- Ensure proper utilization of standard capabilities

### 3.3 Create Custom Entities (Only When Necessary)
- Create custom entities only for requirements that cannot be met by OOTB entities
- Define custom entity structure following hierarchical patterns
- Configure custom entities with appropriate field groups

### 3.4 Configure Field Groups
- Use standard field groups (Address, Phone, Email) where applicable
- Add custom fields to existing field groups when OOTB fields are insufficient
- Create custom field groups only when necessary
- Ensure field groups properly handle 1-to-many relationships

### 3.5 Model Business Requirements
- Design data structures for roles and role-based attributes
- Model entity relationships and relationship attributes
- Create hierarchy structures as specified in requirements
- Ensure relationships support business logic and rules

### 3.6 Design Source System Integration
- Create entity definitions for each source system
- Define attribute mappings from source systems to MDM entities
- Configure cross-reference tracking across source systems
- Document source-to-target field mappings

### 3.7 Ensure Matching, Merging, and Survivorship Support
- Design data model to support matching rules identified in requirements
- Ensure attributes needed for matching are properly modeled
- Structure entities to support merge operations
- Configure survivorship rules at the attribute level

### 3.8 Document the Data Model
- Create comprehensive entity documentation including:
  - Entity definitions and purposes
  - All attributes (OOTB and custom) with descriptions
  - Field groups and their usage
  - Relationships and hierarchies
- Document source system integration patterns
- Document data quality rules and validation requirements
- Include rationale for OOTB usage vs. custom creation decisions

### 3.9 Final Validation
- Verify all requirements from Step 1 are addressed in the model
- Confirm OOTB entities and fields are maximized before custom creation
- Ensure the model follows Informatica MDM SaaS best practices
- Validate hierarchical structure and field group usage

## Validation Checkpoint: Step 3 → Step 4

**MANDATORY**: Complete ALL validations below before proceeding to Step 4. Do NOT proceed if any validation fails.

### ✓ Requirements Coverage Check
- [ ] **All Step 1 requirements addressed**: Every requirement extracted in Step 1 is satisfied in the data model
- [ ] **All entities designed**: Every entity identified in requirements has been designed (OOTB or custom)
- [ ] **All attributes included**: Every required attribute is present in the appropriate entity or field group
- [ ] **All relationships modeled**: Every relationship identified in requirements is represented in the model
- [ ] **All hierarchies designed**: Every hierarchy requirement has been implemented
- [ ] **All roles supported**: Every business role requirement has been accommodated in the data model

### ✓ OOTB Optimization Check
- [ ] **OOTB entities maximized**: All possible OOTB entities (Person, Organization, Product) are used where applicable
- [ ] **OOTB field groups maximized**: All possible OOTB field groups (Address, Phone, Email) are used where applicable
- [ ] **OOTB fields maximized**: All possible OOTB fields within entities and field groups are used before custom fields
- [ ] **Custom fields minimized**: Only absolutely necessary custom fields have been created
- [ ] **Justification documented**: Every custom component has clear justification why OOTB could not be used

### ✓ Model Structure Check
- [ ] **Hierarchical structure**: The model uses proper hierarchical document-style structure
- [ ] **Field groups for 1:M**: All 1-to-many relationships use field groups appropriately
- [ ] **Native patterns followed**: Model follows Informatica MDM SaaS native patterns and best practices
- [ ] **Proper entity organization**: Entities are organized in logical parent-child hierarchy where applicable

### ✓ Source Integration Check
- [ ] **All source systems mapped**: Every source system has entity definitions and attribute mappings
- [ ] **Cross-reference tracking**: Cross-reference tracking is configured for all required fields
- [ ] **Source-to-target mappings**: All source-to-target field mappings are documented
- [ ] **Transformation requirements**: Any transformation requirements have been addressed

### ✓ MDM Capabilities Check
- [ ] **Matching support**: Data model supports all matching rules identified in requirements
- [ ] **Merging support**: Entities are structured to support merge operations
- [ ] **Survivorship configured**: Survivorship rules are defined at the attribute level
- [ ] **Data quality rules**: All data quality rules are documented and supported by the model

### ✓ Documentation Completeness Check
- [ ] **Entity definitions complete**: Every entity has complete definition with purpose
- [ ] **All attributes documented**: Every attribute (OOTB and custom) has description and purpose
- [ ] **Field groups documented**: All field groups and their usage are documented
- [ ] **Relationships documented**: All relationships and hierarchies are documented
- [ ] **Source integration documented**: Source system integration patterns are documented
- [ ] **Data quality rules documented**: All data quality rules and validation requirements are documented
- [ ] **Rationale provided**: Justifications for OOTB vs. custom decisions are included

### ✓ Model Quality Check
- [ ] **No contradictions**: Model is internally consistent with no conflicting structures
- [ ] **Complete and ready**: Model is complete and ready for implementation
- [ ] **Best practices followed**: All Informatica MDM SaaS best practices are followed
- [ ] **Model is implementable**: The documented model can be implemented in Informatica MDM SaaS

### ✓ Approval Gate
- [ ] **All validations passed**: Every checkbox above is marked as complete
- [ ] **Model reviewed**: The complete data model has been reviewed for accuracy and completeness
- [ ] **Ready for visualization**: The model documentation is complete and ready for diagram creation in Step 4

**IF ANY VALIDATION FAILS**: Review and fix the identified issues before proceeding to Step 4.

## Output
A complete, documented MDM data model including:
- Entity definitions (OOTB and custom) with all attributes
- Field groups and their configurations
- Relationship and hierarchy structures
- Source system integration mappings
- Data quality rules and validation requirements
- Complete documentation with justifications for design decisions
- Ready-to-implement model structure for Informatica MDM SaaS

**Next Step**: This output serves as the input for Step 4, where visual hierarchy diagrams will be created for each entity using the documented structure.

