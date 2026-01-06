# Step 2: Map Requirements to OOTB Entities and Identify Gaps

## Objective
Map extracted requirements to Informatica MDM SaaS out-of-the-box (OOTB) entities and field groups, identifying what can be reused and what needs customization.

## Input
Take the comprehensive requirements analysis document from Step 1, which includes:
- All extracted business entities and their purposes
- Required attributes and fields for each entity
- Relationships and hierarchies
- Roles and business rules
- Source system integration requirements
- Matching, merging, and survivorship requirements
- Data quality rules and cross-reference tracking needs
- Organized and categorized functional requirements

## Tasks

### 2.1 Map to Standard OOTB Entities
- **Person Entity**: Check if any extracted entities match Informatica's standard Person entity
- **Organization Entity**: Check if any extracted entities match Informatica's standard Organization entity
- **Product Entity**: Check if any extracted entities match Informatica's standard Product entity
- Document which requirements map to which OOTB entities
- Note any standard entity capabilities that fulfill requirements

### 2.2 Map to Standard OOTB Field Groups
- **Address Field Group**: Check if address-related requirements can use standard Address field group
- **Phone Field Group**: Check if phone/contact requirements can use standard Phone field group
- **Email Field Group**: Check if email requirements can use standard Email field group
- List all standard field groups available and their standard fields
- Document which requirements map to existing field group fields

### 2.3 Review OOTB Entity and Field Group Capabilities
- **CRITICAL INSTRUCTION**: For each requirement from Step 1, follow this mandatory sequence:
  1. **FIRST**: List ALL fields available in the relevant OOTB entity out-of-the-box
  2. **FIRST**: List ALL fields available in the relevant OOTB field groups out-of-the-box
  3. **THEN**: Review each listed OOTB field to see if it can be USED for the requirement
  4. **ONLY AFTER**: If OOTB fields cannot fulfill the requirement, proceed to identify custom field needs
- For each requirement:
  - **MUST FIRST** check if OOTB entities can accommodate it
  - **MUST FIRST** check if OOTB field groups contain applicable fields
  - **MUST FIRST** mention/list all OOTB fields in relevant entities and field groups
  - **MUST FIRST** determine if OOTB fields can be used before considering custom fields
  - **ONLY THEN** document if custom fields are needed when OOTB fields cannot be used

### 2.4 Identify Gaps and Customization Needs
- Document requirements that cannot be met by OOTB entities → **Custom entities needed**
- Document requirements where OOTB field groups lack required fields → **Custom fields needed in field groups**
- Document requirements where OOTB entities need extension → **Custom attributes needed on entities**
- Prioritize extending OOTB entities over creating new entities

### 2.5 Apply Design Principles
- **Use OOTB entities first** - Only create custom entities when absolutely necessary
- **Extend before creating** - Add custom attributes to OOTB entities instead of creating new entities when possible
- **Customize field groups** - Add custom fields to existing field groups rather than creating new field groups
- **CRITICAL**: Do NOT create too many custom fields - First mention all OOTB fields in the entity and see if you can USE THEM, else go on and create custom fields
- Minimize custom fields by maximizing OOTB field usage - Always exhaust OOTB field options before creating custom ones

### 2.6 Create Mapping Documentation
- Create a mapping matrix showing:
  - Requirement → OOTB Entity/Field → Custom Entity/Field (if needed)
  - Justification for using OOTB vs. creating custom components
  - Gaps identified and proposed solutions

## Validation Checkpoint: Step 2 → Step 3

**MANDATORY**: Complete ALL validations below before proceeding to Step 3. Do NOT proceed if any validation fails.

### ✓ OOTB Coverage Check
- [ ] **All OOTB entities evaluated**: Person, Organization, Product entities have been checked against all requirements
- [ ] **All OOTB field groups evaluated**: Address, Phone, Email field groups have been checked for all relevant requirements
- [ ] **All OOTB fields listed**: For each requirement, ALL relevant OOTB fields in entities and field groups have been listed and reviewed
- [ ] **OOTB-first approach verified**: Every requirement has been evaluated against OOTB capabilities before considering custom solutions

### ✓ Mapping Completeness Check
- [ ] **100% requirement coverage**: Every requirement from Step 1 has been mapped (to either OOTB or custom)
- [ ] **All entities mapped**: Every extracted entity has been assigned to either an OOTB entity or marked as custom
- [ ] **All attributes mapped**: Every attribute requirement has been mapped to either OOTB field or custom field
- [ ] **All field groups mapped**: Every 1-to-many requirement has been mapped to either OOTB or custom field group

### ✓ Justification Check
- [ ] **OOTB usage justified**: For each OOTB entity/field used, there is clear justification that it meets the requirement
- [ ] **Custom creation justified**: For each custom entity/field created, there is clear justification that OOTB cannot accommodate it
- [ ] **No unnecessary custom fields**: Verification that custom fields were only created after exhausting OOTB options

### ✓ Gap Analysis Check
- [ ] **Custom entities documented**: All requirements needing custom entities have been identified with clear justification
- [ ] **Custom attributes documented**: All custom attributes needed for OOTB entities have been identified
- [ ] **Custom field groups documented**: All custom field groups needed have been identified with justification
- [ ] **Custom fields in field groups documented**: All custom fields to be added to existing field groups have been listed

### ✓ Design Principles Compliance
- [ ] **OOTB-first principle followed**: OOTB entities and fields are prioritized throughout
- [ ] **Extend-before-create principle followed**: Custom attributes on OOTB entities are preferred over new entities
- [ ] **Field group customization**: Custom fields added to existing field groups before creating new ones
- [ ] **Minimal custom fields**: Only necessary custom fields have been identified

### ✓ Mapping Matrix Quality
- [ ] **Complete mapping matrix**: Requirement → OOTB Entity/Field → Custom Entity/Field mapping is complete
- [ ] **Clear traceability**: Every requirement can be traced through the mapping
- [ ] **Gaps clearly identified**: All gaps have been documented with proposed solutions

### ✓ Approval Gate
- [ ] **All validations passed**: Every checkbox above is marked as complete
- [ ] **Mapping reviewed**: The mapping document has been reviewed for accuracy and completeness
- [ ] **Ready for design**: The mapping is sufficient to proceed with data model design in Step 3

**IF ANY VALIDATION FAILS**: Review and fix the identified issues before proceeding to Step 3.

## Output
A detailed mapping document showing:
- Requirements successfully mapped to OOTB entities and fields
- Gaps identified where customization is needed
- Justification for each OOTB usage vs. custom creation decision
- Clear list of custom entities, custom fields, and custom attributes that will be created in Step 3

**Next Step**: This output serves as the input for Step 3, where the hierarchical data model will be designed and documented based on these mappings.

