# Step 2: Mapping to OOTB Entities and Identifying Gaps

**MDM Focus:** This mapping creates the canonical MDM model structure using OOTB entities. The model represents the unified master data structure, not source-specific schemas. All source systems feed into these canonical entities.

## 2.1 Master Entity Mappings

The following mappings define the canonical MDM entities that will serve as the "golden record" for master data:

### Unified MDM Entity

- **OOTB Entity:** Person
- **Justification:** Consolidated all requirements (Person, Organization) into single OOTB Person entity. Using OOTB entity to minimize customization and leverage standard MDM capabilities. Additional fields added as custom attributes only where OOTB fields cannot accommodate requirements and are justified by functional requirements.
- **Consolidated Requirements:** Person, Organization
- **Custom Fields with FR References:**
  - Classification: FR34
  - Ein: FR3, FR4, FR10
  - Employmentstatus: FR34
  - Relationshiptype: FR2, FR6, FR9, FR10, FR45
  - Roletype: FR21, FR22, FR23, FR41, FR42
  - Status: FR21
- **OOTB Fields Used:** FirstName, LastName, MiddleName, NamePrefix, NameSuffix, FullName, DateOfBirth, Gender, MaritalStatus, PreferredLanguage, DeceasedDate, DeceasedFlag
- **Custom Fields Needed:** Classification, Ein, Employmentstatus, Relationshiptype, Roletype, Status

## 2.2 Field Group Mappings

### Address field group

- **OOTB Field Group:** Address
- **Justification:** Solution shall implement cost effective, centralized standardization approach that standardizes addresses to an uniform format. Solution will leverage...
- **OOTB Fields Used:** AddressLine1, AddressLine2, City, State, PostalCode, Country, AddressType, PrimaryFlag, StartDate, EndDate, County, Region, Latitude, Longitude
- **Custom Fields Needed:** SourceSystemKey

### Phone field group

- **OOTB Field Group:** Phone
- **Justification:** Solution shall implement cost effective, centralized standardization approach that standardizes phone numbers to an uniform format. Solution will leve...
- **OOTB Fields Used:** PhoneNumber, PhoneType, PrimaryFlag, CountryCode, AreaCode, Extension, StartDate, EndDate, DoNotCallFlag
- **Custom Fields Needed:** SourceSystemKey

### Email field group

- **OOTB Field Group:** Email
- **Justification:** Solution shall have ability to identify unique value for each Email record from each source system. That way updates to existing Email from Source wil...
- **OOTB Fields Used:** EmailAddress, EmailType, PrimaryFlag, StartDate, EndDate, DoNotEmailFlag, BounceFlag
- **Custom Fields Needed:** SourceSystemKey

## 2.3 Custom Components Required

### Constituent (CustomFieldGroup)

- **Justification:** MDM shall have ability to accomodate multiple child records of a constituent that are originating from the source systems. i.e. 1:Many phone, email, e...
- **Fields:** Type, Status, StartDate, EndDate, SourceSystem, SourceSystemKey

### Ex (CustomFieldGroup)

- **Justification:** Solution shall replicate and eventually replace current Slate integration into ODS for reporting needs. (Slate - transactional+customer+Nmcustomer) wi...
- **Fields:** Type, Status, StartDate, EndDate, SourceSystem, SourceSystemKey

## 2.4 Mapping Summary

- **OOTB Entities Used:** [List OOTB entities used in your mappings, e.g., Person, Organization, Product]
- **OOTB Field Groups Used:** [List OOTB field groups leveraged, e.g., Address, Phone, Email]
- **Custom Field Groups:** [List any custom field groups required, if applicable]
- **Custom Attributes on OOTB Entities:** [List custom attributes added to OOTB entities, if any]
- **Custom Fields in OOTB Field Groups:** [List custom fields added to OOTB field groups, if any]

