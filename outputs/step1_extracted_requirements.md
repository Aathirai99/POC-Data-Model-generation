# Step 1: Extracted Requirements Analysis

**MDM Focus:** This analysis identifies canonical master data entities for the MDM model. Source systems (Banner, Slate, etc.) are data sources that feed into these master entities, not entities themselves.

**Extraction Date:** 2025-12-22T14:03:13.856832
**Total Requirements Processed:** 45
**Source File:** USF Requirements Document - Phase 0B.xlsx

## 1.1 Master Data Entities Identified

The following are canonical master entities that will be managed in the MDM system. Each entity represents a unified "golden record" that consolidates data from multiple source systems.

- **Constituent** (CustomFieldGroup): MDM shall have ability to accomodate multiple child records of a constituent that are originating from the source systems. i.e. 1:Many phone, email, e...
- **Address** (FieldGroup): Solution shall implement cost effective, centralized standardization approach that standardizes addresses to an uniform format. Solution will leverage...
- **Phone** (FieldGroup): Solution shall implement cost effective, centralized standardization approach that standardizes phone numbers to an uniform format. Solution will leve...
- **Email** (FieldGroup): Solution shall have ability to identify unique value for each Email record from each source system. That way updates to existing Email from Source wil...
- **Ex** (CustomFieldGroup): Solution shall replicate and eventually replace current Slate integration into ODS for reporting needs. (Slate - transactional+customer+Nmcustomer) wi...
- **Organization** (Organization): Solution shall have the ability to pull data that feeds six  out of eleven current tableau reports referenced in the file: https://docs.google.com/spr...
- **Person** (Person): Solution shall have the ability to exclude access to sensitive data elements from source extraction onwards. (within the Blob and downstream). In spec...

## 1.2 Required Attributes and Fields

### Person Entity
**Standard Attributes:**
- FirstName
- LastName
- MiddleName
- NamePrefix
- NameSuffix
- FullName
- DateOfBirth
- Gender
- MaritalStatus
- PreferredLanguage
- DeceasedDate
- DeceasedFlag

**Custom Attributes:**
- Classification
- Ein
- Employmentstatus
- Relationshiptype
- Roletype
- Status


## 1.3 Relationships and Hierarchies

- [Entity] → Address (1-to-many)
- [Entity] → Phone (1-to-many)
- [Entity] → Email (1-to-many)
- [Entity] → Role (1-to-many)
- [Entity] → Relationship (1-to-many)

## 1.4 Roles and Business Rules

- **Prospect**: solution shall have the ability to pull data that feeds six  out of eleven current tableau reports r...
- **Student**: solution shall replicate and eventually replace current slate integration into ods for reporting nee...
- **Customer**: solution shall replicate and eventually replace current slate integration into ods for reporting nee...
- **Alumni**: solution shall replicate and eventually replace current slate integration into ods for reporting nee...
- **User**: solution shall have the ability to replace pidm with cwid in the mdm user interface. (in top left co...
- **Member**: mdm shall have ability to provide access to merge/un-merge to selective it team members. nan...
- **Staff**: solution shall have ability to update servicenow user profile with information from mdm golden recor...

## 1.5 Source System Integration Requirements

- **Banner**: JDBC
- **Workday**: SOAP API
- **Slate**: API
- **Salesforce**: API
- **SFAQ**: API
- **AffinaQuest**: API
- **SF-STU**: API
- **Snowflake**: Database
- **IAM**: API
- **Slack**: API

## 1.6 Matching, Merging, and Survivorship Requirements

- **Address matching**: Match based on standardized address components; may use a unique key from the source system or a composite of address fields.
- **Phone matching**: Match on normalized phone number (country and area code); uniqueness may vary based on business requirements.
- **Email matching**: Match on lowercased, trimmed email address; not always unique depending on real-world usage.
- **Address crosswalk**: Use reference/crosswalk tables to link and translate between keys of source and master addresses.

## 1.7 Data Quality Rules

- **Address standardization**: Centralized standardization to uniform format
- **Phone standardization**: Centralized standardization to uniform format
- **Lookup value mapping**: Map source values to MDM values via reference data
