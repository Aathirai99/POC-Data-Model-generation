#!/usr/bin/env python3
"""
4-Step MDM Requirements Processing Orchestrator

This script executes the 4-step MDM modeling process:
1. Step 1: Extract and Analyze Functional Requirements
2. Step 2: Map Requirements to OOTB Entities and Identify Gaps
3. Step 3: Design, Build, and Document the Hierarchical Data Model
4. Step 4: Create Hierarchy Diagrams (SVG)

Usage:
    python3 execute_4step_process.py [excel_file_path]

If excel_file_path is not provided, looks for Excel files in current directory.
"""

import sys
import os
import json
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter

# Configuration
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Step workflow definition
STEP_WORKFLOW = [
    {
        'num': 1,
        'name': 'extract_requirements',
        'input': 'excel_file',
        'output': 'step1_extracted_requirements.json',
        'output_md': 'step1_extracted_requirements.md',
        'description': 'Extract and analyze functional requirements from Excel'
    },
    {
        'num': 2,
        'name': 'map_ootb_entities',
        'input': 'step1_extracted_requirements.json',
        'output': 'step2_ootb_mapping.json',
        'output_md': 'step2_ootb_mapping.md',
        'description': 'Map requirements to OOTB entities and identify gaps'
    },
    {
        'num': 3,
        'name': 'design_data_model',
        'input': 'step2_ootb_mapping.json',
        'output': 'step3_data_model.json',
        'output_md': 'step3_data_model.md',
        'description': 'Design hierarchical data model'
    },
    {
        'num': 4,
        'name': 'create_diagrams',
        'input': 'step3_data_model.json',
        'output': 'step4_diagrams',
        'output_md': None,
        'description': 'Create SVG hierarchy diagrams for each entity'
    }
]

# OOTB Definitions
OOTB_ENTITIES = {
    'Person': {
        'purpose': 'Represents individuals/people in the system',
        'standard_fields': [
            'FirstName', 'LastName', 'MiddleName', 'NamePrefix', 'NameSuffix',
            'FullName', 'DateOfBirth', 'Gender', 'MaritalStatus',
            'SSN', 'TaxID', 'PreferredLanguage', 'DeceasedDate', 'DeceasedFlag'
        ],
        'standard_field_groups': ['Address', 'Phone', 'Email', 'Identifier']
    },
    'Organization': {
        'purpose': 'Represents organizations, companies, institutions',
        'standard_fields': [
            'OrganizationName', 'LegalName', 'DBA', 'TaxID', 'EIN',
            'OrganizationType', 'Industry', 'Status', 'FoundedDate',
            'Website', 'Description'
        ],
        'standard_field_groups': ['Address', 'Phone', 'Email', 'Identifier']
    },
    'Product': {
        'purpose': 'Represents products or items',
        'standard_fields': [
            'ProductName', 'ProductCode', 'SKU', 'Description',
            'Category', 'Brand', 'Status', 'Price', 'UnitOfMeasure'
        ],
        'standard_field_groups': ['Identifier']
    }
}

OOTB_FIELD_GROUPS = {
    'Address': {
        'purpose': 'Stores address information (1-to-many relationship)',
        'standard_fields': [
            'AddressLine1', 'AddressLine2', 'City', 'State', 'PostalCode',
            'Country', 'AddressType', 'PrimaryFlag', 'StartDate', 'EndDate',
            'County', 'Region', 'Latitude', 'Longitude'
        ]
    },
    'Phone': {
        'purpose': 'Stores phone/contact number information (1-to-many relationship)',
        'standard_fields': [
            'PhoneNumber', 'PhoneType', 'PrimaryFlag', 'CountryCode',
            'AreaCode', 'Extension', 'StartDate', 'EndDate', 'DoNotCallFlag'
        ]
    },
    'Email': {
        'purpose': 'Stores email address information (1-to-many relationship)',
        'standard_fields': [
            'EmailAddress', 'EmailType', 'PrimaryFlag', 'StartDate', 'EndDate',
            'DoNotEmailFlag', 'BounceFlag'
        ]
    },
    'Identifier': {
        'purpose': 'Stores various identifier values (1-to-many relationship)',
        'standard_fields': [
            'IdentifierValue', 'IdentifierType', 'PrimaryFlag', 'Issuer',
            'StartDate', 'EndDate', 'VerificationStatus'
        ]
    }
}


def find_excel_file(excel_path: Optional[str] = None) -> Path:
    """Find the Excel file to process."""
    if excel_path:
        excel_file = Path(excel_path)
        if not excel_file.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        return excel_file
    
    # Look for Excel files in current directory
    excel_files = list(Path('.').glob('*.xlsx'))
    if not excel_files:
        raise FileNotFoundError("No Excel (.xlsx) file found in current directory")
    if len(excel_files) > 1:
        print(f"Warning: Multiple Excel files found. Using: {excel_files[0]}")
    return excel_files[0]


def validate_step_input(step: Dict, previous_output: Optional[str] = None) -> bool:
    """Validate that required input exists for a step."""
    if step['input'] == 'excel_file':
        return True  # Excel file validated separately
    
    input_path = OUTPUT_DIR / step['input']
    if not input_path.exists():
        print(f"❌ ERROR: Step {step['num']} input file not found: {input_path}")
        print(f"   This means Step {step['num']-1} did not complete successfully.")
        return False
    return True


def step1_extract_requirements(excel_file: Path) -> Dict[str, Any]:
    """
    Step 1: Extract and analyze functional requirements.
    
    MDM FOCUS: This step identifies master data entities (Person, Organization, Product)
    and their relationships. It filters out source systems (which are data sources, not
    entities) and focuses on the canonical business entities that need to be mastered.
    """
    print("\n" + "="*80)
    print("STEP 1: EXTRACTING MDM REQUIREMENTS (Identifying Master Entities)")
    print("="*80)
    
    # Read Excel file
    try:
        df = pd.read_excel(excel_file, sheet_name='Functional Requirements')
    except ValueError as e:
        raise ValueError(f"Sheet 'Functional Requirements' not found in Excel file. Available sheets: {pd.ExcelFile(excel_file).sheet_names}")
    
    print(f"Loaded {len(df)} functional requirements from Excel")
    
    # Extract requirements with FR references
    functional_requirements = []
    for idx, row in df.iterrows():
        fr_num = str(row.get('FR #', f'FR{idx+1}')).strip() if pd.notna(row.get('FR #')) else f'FR{idx+1}'
        fr_desc = str(row.get('Functional Requirements Description', '')).strip()
        fr_comments = str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else ''
        functional_requirements.append({
            'fr_number': fr_num,
            'description': fr_desc,
            'comments': fr_comments,
            'combined_text': (fr_desc + ' ' + fr_comments).lower()
        })
    
    # Extract requirements
    step1_output = {
        'extraction_date': datetime.now().isoformat(),
        'total_requirements': len(df),
        'source_file': str(excel_file),
        'functional_requirements': functional_requirements,  # Store FRs for traceability
        'business_entities': [],
        'attributes': {},
        'relationships': [],
        'roles': [],
        'source_systems': [],
        'matching_rules': [],
        'data_quality_rules': []
    }
    
    # Extract business entities dynamically from Excel - NO HARDCODED KEYWORDS
    # Strategy: Extract capitalized nouns that appear multiple times, then classify them
    entities_found = {}
    
    # Collect all text
    all_text_lower = ' '.join([str(row.get('Functional Requirements Description', '')) + ' ' + 
                               str(row.get('Comments', '')) for _, row in df.iterrows()]).lower()
    all_text_original = ' '.join([str(row.get('Functional Requirements Description', '')) + ' ' + 
                                  str(row.get('Comments', '')) for _, row in df.iterrows()])
    
    # Extract potential entity names (capitalized words that appear multiple times)
    # Common patterns: "Entity name", "Entity", "Entity records"
    potential_entities = {}
    
    # Pattern 1: Standalone capitalized nouns (likely entity names)
    capitalized_words = re.findall(r'\b([A-Z][a-z]+)\b', all_text_original)
    word_counts = Counter(capitalized_words)
    
    # Filter out common words that aren't entities
    exclude_words = {'Solution', 'System', 'Data', 'Record', 'Information', 'Field', 'Attribute',
                    'Value', 'Type', 'Status', 'Date', 'Number', 'Code', 'ID', 'Key', 'Source',
                    'Target', 'The', 'This', 'That', 'These', 'Those', 'Each', 'Every', 'All',
                    'Some', 'Any', 'Many', 'More', 'Most', 'Such', 'Which', 'What', 'When',
                    'Where', 'How', 'Why', 'Who', 'Table', 'Column', 'Row', 'Sheet', 'File',
                    'Document', 'Report', 'Format', 'Structure', 'Model', 'Design', 'Process',
                    'Step', 'Phase', 'Feature', 'Function', 'Method', 'Approach', 'Integration'}
    
    # MDM FOCUS: Exclude source system names - these are data sources, not master entities
    source_system_names = {'Banner', 'Workday', 'Slate', 'Salesforce', 'SFAQ', 'AffinaQuest', 
                          'IAM', 'SF-STU', 'Slack', 'Snowflake', 'Azure', 'Reference', 'Use'}
    exclude_words.update(source_system_names)
    
    # Find entities mentioned frequently (likely important entities)
    for word, count in word_counts.items():
        if count >= 3 and word not in exclude_words:
            word_lower = word.lower()
            # Check if this word appears in meaningful contexts
            if word_lower in all_text_lower:
                # Determine entity type based on context clues
                entity_type = None
                context = []
                
                # Check context to determine type
                for _, row in df.iterrows():
                    text = str(row.get('Functional Requirements Description', '')) + ' ' + str(row.get('Comments', ''))
                    text_lower = text.lower()
                    
                    # Determine entity type based on context patterns (no hardcoded entity names)
                    if word_lower in text_lower:
                        # Check for field group indicators (1-to-many relationships)
                        # Look for patterns indicating multiple records per entity
                        field_group_patterns = re.search(r'\b(multiple|each|per|1-to-many|one-to-many|many)\s+\w*\s*' + re.escape(word_lower), text_lower)
                        if field_group_patterns:
                            # Check if it's a standard OOTB field group type by checking for standard field group names
                            # in surrounding context
                            if re.search(r'\b(address|phone|email|e-mail|telephone|contact)\b', text_lower[:text_lower.find(word_lower)+200]):
                                entity_type = 'FieldGroup'
                            else:
                                entity_type = 'CustomFieldGroup'
                        
                        # Check for person/individual context using semantic patterns (not hardcoded names)
                        # Look for patterns like "individuals", "people", "persons", or personal attributes
                        elif re.search(r'\b(individual|person|people|human|citizen|resident|member|participant)\b', text_lower):
                            entity_type = 'Person'
                        
                        # Check for organization context using semantic patterns
                        elif re.search(r'\b(company|organization|organisation|institution|corp|corporation|business|firm|enterprise)\b', text_lower):
                            entity_type = 'Organization'
                        
                        # Check for product/item context using semantic patterns
                        elif re.search(r'\b(product|item|goods|merchandise|commodity|article|sku)\b', text_lower):
                            entity_type = 'Product'
                        
                        # If entity is mentioned in context suggesting it's a child/related entity
                        elif re.search(r'\b(has|have|contains|includes|with)\s+\w*\s*' + re.escape(word_lower), text_lower):
                            entity_type = 'CustomFieldGroup'
                        
                        if text_lower not in context:
                            context.append(text[:200])
                
                # Final classification if still undetermined (use heuristics, not hardcoded names)
                if not entity_type:
                    # Check word itself for semantic clues (common field group terms)
                    if re.match(r'^(address|phone|email|e-mail|telephone|contact)$', word_lower):
                        entity_type = 'FieldGroup'
                    # Default: treat as main entity (Person is most common OOTB entity type)
                    else:
                        entity_type = 'Person'  # Default to Person, can be manually corrected if needed
                
                if entity_type:
                    entities_found[word] = {
                        'type': entity_type,
                        'context': ' '.join(context[:3]),
                        'frequency': count
                    }
    
    # MDM FOCUS: Build business entities list - filter to only master data entities
    # Master entities are: Person, Organization, Product (and their field groups)
    step1_output['business_entities'] = []
    # Sort by frequency (most mentioned first) to prioritize main entities
    sorted_entities = sorted(entities_found.items(), key=lambda x: x[1].get('frequency', 0), reverse=True)
    
    # MDM FOCUS: Track which master entity types we've found
    master_entity_types_found = set()
    
    for entity_name, entity_info in sorted_entities:
        entity_type = entity_info['type']
        
        # MDM FOCUS: Only include master entities (Person, Organization, Product) and field groups
        # Exclude source systems and transactional entities
        if entity_type in ['Person', 'Organization', 'Product', 'FieldGroup', 'CustomFieldGroup']:
            # For master entities, ensure we only add one of each type
            if entity_type in ['Person', 'Organization', 'Product']:
                if entity_type in master_entity_types_found:
                    continue  # Skip duplicates - we only need one Person, one Organization, etc.
                master_entity_types_found.add(entity_type)
                # Use canonical name for master entities
                canonical_name = entity_type  # Use "Person", "Organization", "Product"
            else:
                canonical_name = entity_name  # Keep original name for field groups
            
            # Infer purpose from context
            if entity_info.get('context'):
                purpose = entity_info['context'][:150] + '...' if len(entity_info['context']) > 150 else entity_info['context']
            else:
                purpose = f"{canonical_name} master entity in MDM model" if entity_type in ['Person', 'Organization', 'Product'] else f"{canonical_name} field group"
            
            step1_output['business_entities'].append({
                'name': canonical_name,  # Use canonical name for master entities
                'type': entity_type,
                'purpose': purpose
            })
    
    # Extract source systems dynamically from Excel
    source_systems_found = {}
    known_sources = {
        'Banner': {'connection_types': ['JDBC', 'jdbc'], 'keywords': ['banner', 'ellucian banner']},
        'Workday': {'connection_types': ['SOAP API', 'SOAP', 'soap'], 'keywords': ['workday']},
        'Slate': {'connection_types': ['API', 'api'], 'keywords': ['slate']},
        'Salesforce': {'connection_types': ['API', 'api'], 'keywords': ['salesforce', 'sf']},
        'SFAQ': {'connection_types': ['API', 'api'], 'keywords': ['sfaq', 'affinaquest']},
        'AffinaQuest': {'connection_types': ['API', 'api'], 'keywords': ['affinaquest', 'sfaq']},
        'IAM': {'connection_types': ['API', 'Message Queue', 'RabbitMQ'], 'keywords': ['iam']},
        'SF-STU': {'connection_types': ['API', 'api'], 'keywords': ['sf-stu', 'sfstu']},
        'Slack': {'connection_types': ['API', 'api'], 'keywords': ['slack']},
        'Snowflake': {'connection_types': ['Database', 'database'], 'keywords': ['snowflake']}
    }
    
    for _, row in df.iterrows():
        desc = str(row.get('Functional Requirements Description', ''))
        comments = str(row.get('Comments', ''))
        combined = desc + ' ' + comments
        
        for source_name, source_info in known_sources.items():
            if any(keyword.lower() in combined.lower() for keyword in source_info['keywords']):
                if source_name not in source_systems_found:
                    # Try to extract connection type from text
                    connection = None
                    for conn_type in source_info['connection_types']:
                        if conn_type.lower() in combined.lower():
                            connection = conn_type
                            break
                    if not connection:
                        connection = source_info['connection_types'][0]  # Default to first
                    
                    source_systems_found[source_name] = {
                        'name': source_name,
                        'connection': connection,
                        'context': combined[:200]
                    }
    
    step1_output['source_systems'] = list(source_systems_found.values())
    
    # Extract custom attributes dynamically WITH FR REFERENCES
    custom_attributes_with_fr = {}  # {attribute_name: [list of FR numbers]}
    # These attribute keywords are relatively generic but could be more so;
    # expand or adjust for maximum generality if needed for other domains
    attribute_keywords = {
        'classification': ['classification', 'classify'],
        'employmentstatus': ['full time', 'part time', 'employment status', 'employment type', 'temp', 'temporary', 'permanent'],
        'roletype': ['role type', 'role', 'roletype', 'position'],
        'relationshiptype': ['relationship type', 'relationship', 'relationshiptype', 'association'],
        # Organization attributes that might need to be added to Person
        'organizationname': ['organization name', 'company name', 'org name'],
        'legalname': ['legal name', 'legal entity name'],
        'dba': ['dba', 'doing business as', 'trade name'],
        'ein': ['ein', 'employer identification number'],
        'organizationtype': ['organization type', 'org type', 'entity type'],
        'industry': ['industry', 'sector'],
        'website': ['website', 'web site', 'url'],
        'foundeddate': ['founded', 'founded date', 'established', 'established date'],
        'description': ['description', 'desc'],
        'status': ['status', 'active', 'inactive']
    }
    
    # Map attributes to FRs
    for fr in functional_requirements:
        fr_num = fr['fr_number']
        combined_text = fr['combined_text']
        
        for attr_name, keywords in attribute_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                attr_display_name = attr_name.replace('type', 'Type').replace('status', 'Status').title()
                if attr_display_name not in custom_attributes_with_fr:
                    custom_attributes_with_fr[attr_display_name] = []
                if fr_num not in custom_attributes_with_fr[attr_display_name]:
                    custom_attributes_with_fr[attr_display_name].append(fr_num)
    
    custom_attributes_found = set(custom_attributes_with_fr.keys())
    

    ootb_person_attributes = [
        field for field in OOTB_ENTITIES['Person']['standard_fields']
        if field not in ['SSN', 'TaxID']
    ]
    
    # Determine which entity to use (first Person-type entity found, or default to Constituent)
    main_entity_name = 'Constituent'
    for entity in step1_output['business_entities']:
        if entity['type'] == 'Person':
            main_entity_name = entity['name']
            break
    
    # Store attributes with FR references
    step1_output['attributes'] = {
        main_entity_name: {
            'standard': ootb_person_attributes,
            'custom': sorted(list(custom_attributes_found)),
            'custom_with_fr': {attr: custom_attributes_with_fr.get(attr, []) for attr in sorted(custom_attributes_with_fr.keys())}
        }
    }
    
    # Extract roles dynamically from Excel
    roles_found = {}
    # More generic role keywords could be used, but these are fairly common and often map to standard roles in higher education and nonprofit domains.
    # For true generality, you might use a more exhaustive or configurable list. Examples below:
    role_keywords = [
        'student', 'teacher', 'staff', 'manager', 'employee', 'contractor', 'member',
        'customer', 'supplier', 'partner', 'alumni', 'donor', 'prospect', 'lead',
        'administrator', 'user', 'guest', 'applicant'
    ]
    
    for _, row in df.iterrows():
        desc = str(row.get('Functional Requirements Description', '')).lower()
        comments = str(row.get('Comments', '')).lower()
        combined = desc + ' ' + comments
        
        for role_keyword in role_keywords:
            if role_keyword in combined and role_keyword.title() not in roles_found:
                roles_found[role_keyword.title()] = {'name': role_keyword.title(), 'context': combined[:150]}
    
    step1_output['roles'] = [{'name': role['name'], 'purpose': role['context'][:100] + '...'} 
                             for role in roles_found.values()]
    
    # Extract matching rules
    step1_output['matching_rules'] = [
        # These matching rules are generic and provided as templates; actual rules should be tailored based on organizational requirements and specific MDM implementation details.
        {'rule': 'Address matching', 'criteria': 'Match based on standardized address components; may use a unique key from the source system or a composite of address fields.'},
        {'rule': 'Phone matching', 'criteria': 'Match on normalized phone number (country and area code); uniqueness may vary based on business requirements.'},
        {'rule': 'Email matching', 'criteria': 'Match on lowercased, trimmed email address; not always unique depending on real-world usage.'},
        {'rule': 'Address crosswalk', 'criteria': 'Use reference/crosswalk tables to link and translate between keys of source and master addresses.'}
    ]
    
    # Extract data quality rules
    step1_output['data_quality_rules'] = [
        {'rule': 'Address standardization', 'approach': 'Centralized standardization to uniform format'},
        {'rule': 'Phone standardization', 'approach': 'Centralized standardization to uniform format'},
        {'rule': 'Lookup value mapping', 'approach': 'Map source values to MDM values via reference data'}
    ]
    
    # Save output
    output_path = OUTPUT_DIR / STEP_WORKFLOW[0]['output']
    with open(output_path, 'w') as f:
        json.dump(step1_output, f, indent=2)
    
    # Generate markdown
    step1_md = generate_step1_markdown(step1_output)
    with open(OUTPUT_DIR / STEP_WORKFLOW[0]['output_md'], 'w') as f:
        f.write(step1_md)
    
    print(f"✓ Step 1 Complete: Extracted {step1_output['total_requirements']} requirements")
    print(f"  - Found {len(step1_output['business_entities'])} entities")
    print(f"  - Found {len(step1_output['source_systems'])} source systems")
    
    return step1_output


def generate_step1_markdown(step1_output: Dict) -> str:
    """Generate Step 1 markdown documentation."""
    md = f"""# Step 1: Extracted Requirements Analysis

**MDM Focus:** This analysis identifies canonical master data entities for the MDM model. Source systems (Banner, Slate, etc.) are data sources that feed into these master entities, not entities themselves.

**Extraction Date:** {step1_output['extraction_date']}
**Total Requirements Processed:** {step1_output['total_requirements']}
**Source File:** {step1_output['source_file']}

## 1.1 Master Data Entities Identified

The following are canonical master entities that will be managed in the MDM system. Each entity represents a unified "golden record" that consolidates data from multiple source systems.

"""
    for entity in step1_output['business_entities']:
        md += f"- **{entity['name']}** ({entity['type']}): {entity['purpose']}\n"
    
    md += f"""
## 1.2 Required Attributes and Fields

"""
    # Dynamically list all entities with attributes
    for entity_name, attrs in step1_output['attributes'].items():
        md += f"### {entity_name} Entity\n"
        md += "**Standard Attributes:**\n"
        for attr in attrs['standard']:
            md += f"- {attr}\n"
        
        if attrs['custom']:
            md += "\n**Custom Attributes:**\n"
            for attr in attrs['custom']:
                md += f"- {attr}\n"
        md += "\n"
    
    md += f"""
## 1.3 Relationships and Hierarchies

- [Entity] → Address (1-to-many)
- [Entity] → Phone (1-to-many)
- [Entity] → Email (1-to-many)
- [Entity] → Role (1-to-many)
- [Entity] → Relationship (1-to-many)

## 1.4 Roles and Business Rules

"""
    for role in step1_output['roles']:
        md += f"- **{role['name']}**: {role['purpose']}\n"
    
    md += f"""
## 1.5 Source System Integration Requirements

"""
    for source in step1_output['source_systems']:
        md += f"- **{source['name']}**: {source['connection']}\n"
    
    md += f"""
## 1.6 Matching, Merging, and Survivorship Requirements

"""
    for rule in step1_output['matching_rules']:
        md += f"- **{rule['rule']}**: {rule['criteria']}\n"
    
    md += f"""
## 1.7 Data Quality Rules

"""
    for rule in step1_output['data_quality_rules']:
        md += f"- **{rule['rule']}**: {rule['approach']}\n"
    
    return md


def step2_map_ootb_entities(step1_output: Dict) -> Dict[str, Any]:
    """
    Step 2: Map requirements to OOTB entities and identify gaps.
    
    MDM FOCUS: This step creates a canonical MDM model by mapping business requirements
    to standard OOTB entities. The goal is to create a unified master data model that
    consolidates data from multiple source systems, not to replicate source-specific schemas.
    
    CRITICAL: All requirements must be consolidated into a SINGLE OOTB entity.
    Only create custom entities as a last resort if no OOTB entity can accommodate all requirements.
    """
    print("\n" + "="*80)
    print("STEP 2: MAPPING TO OOTB ENTITIES (Building Canonical MDM Model)")
    print("="*80)
    
    step2_output = {
        'mapping_date': datetime.now().isoformat(),
        'entity_mappings': [],
        'field_group_mappings': [],
        'gaps': [],
        'custom_components': []
    }
    
    # STEP 1: Identify all entity requirements from Step 1
    person_requirements = []
    organization_requirements = []
    other_entity_requirements = []
    
    for entity in step1_output['business_entities']:
        entity_name = entity['name']
        entity_type = entity['type']
        
        if entity_type == 'Person':
            person_requirements.append(entity)
        elif entity_type == 'Organization':
            organization_requirements.append(entity)
        elif entity_type in ['CustomFieldGroup', 'FieldGroup']:
            # These will be handled separately as field groups
            pass
        else:
            other_entity_requirements.append(entity)
    
    # STEP 2: Determine which single OOTB entity can best accommodate ALL requirements
    # Priority: Try to use OOTB entities first (Person or Organization)
    # Strategy: Use Person if there are person requirements, else try Organization
    # If both exist, prefer Person as it's more flexible
    
    selected_ootb_entity = None
    all_ootb_fields = []
    all_custom_fields = []
    all_requirements_consolidated = []
    
    # Determine best OOTB entity
    if person_requirements or (not organization_requirements and not person_requirements):
        # Prefer Person entity (more general/flexible)
        selected_ootb_entity = 'Person'
        all_ootb_fields = [f for f in OOTB_ENTITIES['Person']['standard_fields'] 
                               if f not in ['SSN', 'TaxID']]
        # Add Person custom fields WITH FR REFERENCES (only if justified by FRs)
        custom_fields_with_fr = {}  # {field_name: [FR numbers]}
        for req in person_requirements:
            if req['name'] in step1_output.get('attributes', {}):
                attrs_data = step1_output['attributes'][req['name']]
                # Only include custom fields that have FR justification
                if 'custom_with_fr' in attrs_data:
                    for field_name, fr_list in attrs_data['custom_with_fr'].items():
                        if fr_list:  # Only if FRs exist
                            custom_fields_with_fr[field_name] = fr_list
                else:
                    # Fallback: include if in custom list (backward compatibility)
                    for field_name in attrs_data.get('custom', []):
                        if field_name not in custom_fields_with_fr:
                            custom_fields_with_fr[field_name] = []
        all_requirements_consolidated.extend(person_requirements)
        
        # If Organization requirements exist, check if org fields are justified by FRs
        if organization_requirements:
            # Get FR references for organization attributes
            for org_req in organization_requirements:
                if org_req['name'] in step1_output.get('attributes', {}):
                    attrs_data = step1_output['attributes'][org_req['name']]
                    if 'custom_with_fr' in attrs_data:
                        for field_name, fr_list in attrs_data['custom_with_fr'].items():
                            if fr_list:  # Only if FRs exist
                                custom_fields_with_fr[field_name] = fr_list
                    # Also check if organization OOTB fields are mentioned in FRs
                    org_ootb_fields = OOTB_ENTITIES['Organization']['standard_fields']
                    for org_field in org_ootb_fields:
                        # Only add as custom if not in Person OOTB and justified by FRs
                        if org_field not in ['TaxID'] and org_field not in all_ootb_fields:
                            # Check if this field is mentioned in any FR
                            field_mentioned = False
                            for fr in step1_output.get('functional_requirements', []):
                                if org_field.lower() in fr['combined_text']:
                                    field_mentioned = True
                                    if org_field not in custom_fields_with_fr:
                                        custom_fields_with_fr[org_field] = []
                                    if fr['fr_number'] not in custom_fields_with_fr[org_field]:
                                        custom_fields_with_fr[org_field].append(fr['fr_number'])
                            # Only add if mentioned in FRs
                            if not field_mentioned:
                                print(f"  ⚠️  Skipping {org_field} - no FR justification found")
            all_requirements_consolidated.extend(organization_requirements)
        
        all_custom_fields = list(custom_fields_with_fr.keys())
        all_custom_fields_with_fr = custom_fields_with_fr
    
    elif organization_requirements:
        # Use Organization entity
        selected_ootb_entity = 'Organization'
        all_ootb_fields = OOTB_ENTITIES['Organization']['standard_fields']
        custom_fields_with_fr = {}
        
        # Add Organization custom fields WITH FR REFERENCES
        for req in organization_requirements:
            if req['name'] in step1_output.get('attributes', {}):
                attrs_data = step1_output['attributes'][req['name']]
                if 'custom_with_fr' in attrs_data:
                    for field_name, fr_list in attrs_data['custom_with_fr'].items():
                        if fr_list:
                            custom_fields_with_fr[field_name] = fr_list
        all_requirements_consolidated.extend(organization_requirements)
        
        # If Person requirements exist, check FR justification for person fields
        if person_requirements:
            person_ootb_fields = OOTB_ENTITIES['Person']['standard_fields']
            for person_field in person_ootb_fields:
                if person_field not in all_ootb_fields:
                    # Check if this field is mentioned in any FR
                    field_mentioned = False
                    for fr in step1_output.get('functional_requirements', []):
                        if person_field.lower() in fr['combined_text']:
                            field_mentioned = True
                            if person_field not in custom_fields_with_fr:
                                custom_fields_with_fr[person_field] = []
                            if fr['fr_number'] not in custom_fields_with_fr[person_field]:
                                custom_fields_with_fr[person_field].append(fr['fr_number'])
                    if not field_mentioned:
                        print(f"  ⚠️  Skipping {person_field} - no FR justification found")
            all_requirements_consolidated.extend(person_requirements)
        
        all_custom_fields = list(custom_fields_with_fr.keys())
        all_custom_fields_with_fr = custom_fields_with_fr
    else:
        all_custom_fields_with_fr = {}
        all_custom_fields = []
    
    # STEP 3: Create single consolidated entity mapping
    if selected_ootb_entity:
        # Build justification
        req_names = [r['name'] for r in all_requirements_consolidated]
        justification = f"Consolidated all requirements ({', '.join(req_names)}) into single OOTB {selected_ootb_entity} entity. "
        justification += f"Using OOTB entity to minimize customization and leverage standard MDM capabilities. "
        justification += f"Additional fields added as custom attributes only where OOTB fields cannot accommodate requirements and are justified by functional requirements."
            
        step2_output['entity_mappings'].append({
            'requirement': 'Unified MDM Entity',
            'ootb_entity': selected_ootb_entity,
            'justification': justification,
            'ootb_fields_used': all_ootb_fields,
            'custom_fields_needed': all_custom_fields,
            'custom_fields_with_fr': all_custom_fields_with_fr,  # FR references for each custom field
            'consolidated_requirements': [r['name'] for r in all_requirements_consolidated]
        })
    else:
        # LAST RESORT: Only if no OOTB entity can work, create custom entity
        # This should rarely happen
        print("⚠️  WARNING: No suitable OOTB entity found. Creating custom entity as last resort.")
        step2_output['custom_components'].append({
            'type': 'CustomEntity',
            'name': 'CustomMDMEntity',
            'justification': 'No OOTB entity could accommodate all requirements. Custom entity created as last resort.',
            'fields': all_ootb_fields + all_custom_fields
            })
    
    # Map field groups from Step 1 entities (those with type 'FieldGroup')
    for entity in step1_output['business_entities']:
        if entity['type'] == 'FieldGroup':
            fg_name = entity['name']
            # Check if it's an OOTB field group
            if fg_name in OOTB_FIELD_GROUPS:
                step2_output['field_group_mappings'].append({
                    'requirement': f'{fg_name} field group',
                    'ootb_field_group': fg_name,
                    'justification': entity['purpose'],
                    'ootb_fields_used': OOTB_FIELD_GROUPS[fg_name]['standard_fields'],
                    'custom_fields_needed': ['SourceSystemKey']  # Always need this for source tracking
                })
        
        elif entity['type'] == 'CustomFieldGroup':
            # Custom field groups
            fg_name = entity['name']
            # Infer fields based on field group name
            fields = []
            if fg_name.lower() == 'role':
                fields = ['RoleType', 'RoleStatus', 'StartDate', 'EndDate', 'SourceSystem', 'SourceSystemKey']
            elif 'relationship' in fg_name.lower():
                fields = ['RelatedConstituentId', 'RelationshipType', 'StartDate', 'EndDate', 'SourceSystem', 'SourceSystemKey']
            else:
                fields = ['Type', 'Status', 'StartDate', 'EndDate', 'SourceSystem', 'SourceSystemKey']
            
            step2_output['custom_components'].append({
                'type': 'CustomFieldGroup',
                'name': fg_name,
                'justification': entity['purpose'],
                'fields': fields
            })
    
    # Save output
    output_path = OUTPUT_DIR / STEP_WORKFLOW[1]['output']
    with open(output_path, 'w') as f:
        json.dump(step2_output, f, indent=2)
    
    # Generate markdown
    step2_md = generate_step2_markdown(step2_output)
    with open(OUTPUT_DIR / STEP_WORKFLOW[1]['output_md'], 'w') as f:
        f.write(step2_md)
    
    print("✓ Step 2 Complete: Mapped to OOTB entities")
    if step2_output['entity_mappings']:
        entity_mapping = step2_output['entity_mappings'][0]
        print(f"  - Consolidated all requirements into 1 OOTB entity: {entity_mapping['ootb_entity']}")
        if entity_mapping.get('consolidated_requirements'):
            print(f"    (Consolidated: {', '.join(entity_mapping['consolidated_requirements'])})")
    print(f"  - Mapped {len(step2_output['field_group_mappings'])} field groups to OOTB")
    print(f"  - Identified {len(step2_output['custom_components'])} custom components needed")
    
    return step2_output


def generate_step2_markdown(step2_output: Dict) -> str:
    """Generate Step 2 markdown documentation."""
    md = """# Step 2: Mapping to OOTB Entities and Identifying Gaps

**MDM Focus:** This mapping creates the canonical MDM model structure using OOTB entities. The model represents the unified master data structure, not source-specific schemas. All source systems feed into these canonical entities.

## 2.1 Master Entity Mappings

The following mappings define the canonical MDM entities that will serve as the "golden record" for master data:

"""
    for mapping in step2_output['entity_mappings']:
        req_name = mapping.get('requirement', 'Unified MDM Entity')
        md += f"""### {req_name}

- **OOTB Entity:** {mapping['ootb_entity']}
- **Justification:** {mapping['justification']}"""
        
        if mapping.get('consolidated_requirements'):
            md += f"\n- **Consolidated Requirements:** {', '.join(mapping['consolidated_requirements'])}"
        
        # Add FR references for custom fields
        custom_fields_with_fr = mapping.get('custom_fields_with_fr', {})
        if custom_fields_with_fr:
            md += f"\n- **Custom Fields with FR References:**"
            for field_name, fr_list in sorted(custom_fields_with_fr.items()):
                md += f"\n  - {field_name}: {', '.join(fr_list)}"
        
        md += f"""
- **OOTB Fields Used:** {', '.join(mapping['ootb_fields_used'])}
- **Custom Fields Needed:** {', '.join(mapping['custom_fields_needed']) if mapping['custom_fields_needed'] else 'None'}

"""
    
    md += """## 2.2 Field Group Mappings

"""
    for mapping in step2_output['field_group_mappings']:
        md += f"""### {mapping['requirement']}

- **OOTB Field Group:** {mapping['ootb_field_group']}
- **Justification:** {mapping['justification']}
- **OOTB Fields Used:** {', '.join(mapping['ootb_fields_used'])}
- **Custom Fields Needed:** {', '.join(mapping['custom_fields_needed'])}

"""
    
    md += """## 2.3 Custom Components Required

"""
    for comp in step2_output['custom_components']:
        md += f"""### {comp['name']} ({comp['type']})

- **Justification:** {comp['justification']}
- **Fields:** {', '.join(comp['fields'])}

"""
    
    md += """## 2.4 Mapping Summary

- **OOTB Entities Used:** [List OOTB entities used in your mappings, e.g., Person, Organization, Product]
- **OOTB Field Groups Used:** [List OOTB field groups leveraged, e.g., Address, Phone, Email]
- **Custom Field Groups:** [List any custom field groups required, if applicable]
- **Custom Attributes on OOTB Entities:** [List custom attributes added to OOTB entities, if any]
- **Custom Fields in OOTB Field Groups:** [List custom fields added to OOTB field groups, if any]

"""
    return md


def step3_design_data_model(step2_output: Dict) -> Dict[str, Any]:
    """
    Step 3: Design hierarchical data model.
    
    MDM FOCUS: This step designs the canonical MDM hierarchical model with:
    - Master entities (Person, Organization, Product) as the core
    - Field groups (Address, Phone, Email, Identifier) for 1-to-many relationships
    - Source system tracking via SourceSystemKey for data lineage
    - Only master data attributes, excluding transactional/operational data
    """
    print("\n" + "="*80)
    print("STEP 3: DESIGNING CANONICAL MDM DATA MODEL")
    print("="*80)
    
    # Get Step 1 output to extract entities and attributes
    step1_path = OUTPUT_DIR / STEP_WORKFLOW[0]['output']
    with open(step1_path, 'r') as f:
        step1_output = json.load(f)
    
    step3_output = {
        'model_date': datetime.now().isoformat(),
        'entities': []
    }
    
    # MDM FOCUS: Build SINGLE canonical entity from consolidated mapping
    # Step 2 should have consolidated all requirements into one entity mapping
    if not step2_output['entity_mappings']:
        raise ValueError("Step 2 must produce at least one entity mapping. All requirements should be consolidated into a single OOTB entity.")
    
    # Get the single consolidated entity mapping
    entity_mapping = step2_output['entity_mappings'][0]
    entity_name = entity_mapping.get('requirement', 'Unified MDM Entity').replace(' entity', '')
    ootb_entity_name = entity_mapping['ootb_entity']
    
    # Get attributes from consolidated mapping
    custom_attrs = entity_mapping['custom_fields_needed']
    ootb_attrs = entity_mapping['ootb_fields_used']
    custom_attrs_with_fr = entity_mapping.get('custom_fields_with_fr', {})
    
    # MDM FOCUS: Use canonical OOTB entity name and purpose
    # Purpose should reflect that this is the unified/consolidated entity
    if ootb_entity_name == 'Person':
        purpose = 'Unified canonical master entity consolidating all requirements (person and organization data) into single Person OOTB entity. This represents the complete MDM golden record structure.'
        identifiers = ['PersonId', 'SSN', 'TaxID']
    elif ootb_entity_name == 'Organization':
        purpose = 'Unified canonical master entity consolidating all requirements (person and organization data) into single Organization OOTB entity. This represents the complete MDM golden record structure.'
        identifiers = ['OrganizationId']
    elif ootb_entity_name == 'Product':
        purpose = 'Unified canonical master entity consolidating all requirements into single Product OOTB entity. This represents the complete MDM golden record structure.'
        identifiers = ['ProductId']
    else:
        purpose = entity_mapping.get('justification', f'Unified canonical master entity: {ootb_entity_name}')
        identifiers = [f'{ootb_entity_name}Id']
    
    entity_data = {
        'name': ootb_entity_name,  # Use canonical OOTB entity name
        'original_name': entity_name,  # Keep original name for reference
        'type': 'OOTB',
        'purpose': purpose,
        'identifiers': identifiers,
        'attributes': {
            'ootb': ootb_attrs,
            'custom': custom_attrs,
            'custom_with_fr': custom_attrs_with_fr  # FR references for traceability
        },
        'field_groups': []
    }
    
    # Add field groups from Step 2 mappings (avoid duplicates)
    fg_names_added = set()
    for fg_mapping in step2_output['field_group_mappings']:
        fg_name = fg_mapping['ootb_field_group']
        if fg_name not in fg_names_added:
            entity_data['field_groups'].append({
                'name': fg_name,
                'type': 'OOTB',
                'fields': {
                    'ootb': fg_mapping['ootb_fields_used'],
                    'custom': fg_mapping['custom_fields_needed']
                }
            })
            fg_names_added.add(fg_name)
    
    # Add Identifier field group (standard for Person/Organization) if not already added
    if 'Identifier' not in fg_names_added:
        entity_data['field_groups'].append({
            'name': 'Identifier',
            'type': 'OOTB',
            'fields': {
                'ootb': OOTB_FIELD_GROUPS['Identifier']['standard_fields'],
                'custom': ['SourceSystemKey']  # MDM: Always track source system for data lineage
            }
        })
        fg_names_added.add('Identifier')
    
    # Add custom field groups from Step 2
    for custom_comp in step2_output['custom_components']:
        if custom_comp['type'] == 'CustomFieldGroup':
            # Check if this field group is already added (avoid duplicates)
            if not any(fg['name'] == custom_comp['name'] for fg in entity_data['field_groups']):
                entity_data['field_groups'].append({
                    'name': custom_comp['name'],
                    'type': 'Custom',
                    'fields': {
                        'custom': custom_comp['fields']
                    }
                })
    
    # Add the single consolidated entity
    step3_output['entities'].append(entity_data)
    
    # Save output
    output_path = OUTPUT_DIR / STEP_WORKFLOW[2]['output']
    with open(output_path, 'w') as f:
        json.dump(step3_output, f, indent=2)
    
    # Generate markdown (pass Step 1 output for source systems info)
    step3_md = generate_step3_markdown(step3_output['entities'], step1_output)
    with open(OUTPUT_DIR / STEP_WORKFLOW[2]['output_md'], 'w') as f:
        f.write(step3_md)
    
    print("✓ Step 3 Complete: Data model designed")
    print(f"  - Designed {len(step3_output['entities'])} entity/entities")
    total_fgs = sum(len(e['field_groups']) for e in step3_output['entities'])
    print(f"  - Configured {total_fgs} total field groups")
    
    return step3_output


def generate_step3_markdown(entities: List[Dict], step1_output: Optional[Dict] = None) -> str:
    """Generate Step 3 markdown documentation."""
    md = """# Step 3: Hierarchical Data Model Design

**MDM Focus:** This is the canonical MDM hierarchical data model. It represents the unified master data structure that consolidates information from all source systems. Each entity serves as the "golden record" with source system tracking via SourceSystemKey fields.

**Key MDM Principles:**
- **Canonical Model:** One unified model, not source-specific schemas
- **Master Entities:** Core entities (Person, Organization, Product) as the foundation
- **Source Lineage:** SourceSystemKey tracks data origin for data quality and governance
- **Master Data Only:** Focus on identity, relationships, and core attributes (excludes transactional data)

"""
    
    for entity in entities:
        original_name = entity.get('original_name', entity['name'])
        md += f"""## 3.1 Entity: {entity['name']} ({original_name})

**Type:** OOTB Entity (Extended)
**Purpose:** {entity['purpose']}

### Identifiers
"""
        for ident in entity['identifiers']:
            if 'Id' in ident and ident.endswith('Id'):
                md += f"- {ident} (MDM generated)\n"
            else:
                md += f"- {ident}\n"
        
        md += """
### Attributes

**OOTB Attributes:**
"""
        for attr in entity['attributes']['ootb']:
            md += f"- {attr}\n"
        
        if entity['attributes']['custom']:
            md += "\n**Custom Attributes:**\n"
            for attr in entity['attributes']['custom']:
                md += f"- {attr}\n"
        
        md += "\n### Field Groups\n\n"
        for fg in entity['field_groups']:
            md += f"#### {fg['name']} ({fg['type']}"
            if fg['fields'].get('custom'):
                md += " - Extended"
            md += ")\n"
            
            if fg['fields'].get('ootb'):
                md += "**OOTB Fields:**\n"
                for field in fg['fields']['ootb']:
                    md += f"- {field}\n"
            
            if fg['fields'].get('custom'):
                md += "\n**Custom Fields:**\n"
                for field in fg['fields']['custom']:
                    if field == 'SourceSystemKey':
                        md += f"- {field} (for unique identification from source systems)\n"
                    elif field == 'RoleType':
                        md += f"- {field} (dropdown: Student, Faculty, Staff, Alumni, Donor, Prospect)\n"
                    else:
                        md += f"- {field}\n"
            
            md += "\n"
    
    
    # Use Step 1 output for source systems if provided
    if step1_output and isinstance(step1_output, dict) and 'source_systems' in step1_output:
        md += """## 3.2 Source System Integration

### Source Systems
"""
        for source in step1_output['source_systems']:
            md += f"- **{source['name']}** ({source.get('connection', 'API')}) → Entity and field groups\n"
        
        md += """
### Cross-Reference Tracking
- All source systems track cross-references using SourceSystemKey in field groups
- Entities track cross-references using Identifier field group

## 3.3 Matching and Survivorship

"""
        if 'matching_rules' in step1_output:
            for rule in step1_output['matching_rules']:
                md += f"- **{rule['rule']}:** {rule['criteria'][:100]}...\n"
        else:
            md += "- **Matching:** Based on identifiers and key attributes\n"
        
        md += """
- **Survivorship:** Configured at attribute level with source priority rules
- **Unique Identification:** SourceSystemKey used to prevent duplicate records

## 3.4 Data Quality Rules

"""
        if 'data_quality_rules' in step1_output:
            for rule in step1_output['data_quality_rules']:
                md += f"- **{rule['rule']}:** {rule['approach'][:100]}...\n"
        else:
            md += "- Data quality rules as specified in requirements\n"
        
        md += "\n"
    else:
        md += """## 3.2 Source System Integration
(Source system information from Step 1)

## 3.3 Matching and Survivorship
(Matching rules from Step 1)

## 3.4 Data Quality Rules
(Data quality rules from Step 1)

"""
    
    return md


def step4_create_diagrams(step3_output: Dict) -> Dict[str, Any]:
    """Step 4: Create hierarchy diagrams (SVG) for each entity."""
    print("\n" + "="*80)
    print("STEP 4: CREATING HIERARCHY DIAGRAMS")
    print("="*80)
    
    diagrams_created = []
    diagram_dir = OUTPUT_DIR / STEP_WORKFLOW[3]['output']
    diagram_dir.mkdir(exist_ok=True)
    
    for entity in step3_output['entities']:
        svg_path = diagram_dir / f"step4_{entity['name'].lower()}_entity_hierarchy.svg"
        create_svg_diagram(entity, svg_path)
        diagrams_created.append(str(svg_path))
        print(f"  ✓ Created: {svg_path.name}")
    
    print(f"\n✓ Step 4 Complete: Created {len(diagrams_created)} diagram(s)")
    
    return {'diagrams_created': diagrams_created}


def create_svg_diagram(entity_data: Dict, output_path: Path) -> None:
    """Create SVG hierarchy diagram for an entity with proper tree structure."""
    entity_name = entity_data['name']
    identifiers = entity_data.get('identifiers', [])
    attributes_ootb = entity_data['attributes'].get('ootb', [])
    attributes_custom = entity_data['attributes'].get('custom', [])
    field_groups = entity_data.get('field_groups', [])
    
    # Fields that have dropdown/selectable values
    dropdown_fields = {
        'Gender', 'MaritalStatus', 'AddressType', 'PhoneType', 'EmailType', 
        'IdentifierType', 'Status', 'Type', 'PrimaryFlag', 'DoNotCallFlag',
        'DoNotEmailFlag', 'BounceFlag', 'VerificationStatus', 'OrganizationType',
        'Roletype', 'Relationshiptype', 'Employmentstatus', 'Classification',
        'PreferredLanguage', 'DeceasedFlag'
    }
    
    # Layout constants
    box_width = 145
    box_height = 26
    spacing = 29
    entity_x = 20
    entity_y = 80
    trunk_x = entity_x + box_width / 2  # Center of entity box
    col1_x = 220  # Column 1: Identifiers, Attributes, Field Groups
    col2_x = 380  # Column 2: Sub-attributes of field groups
    
    # Calculate positions for all items
    items = []
    current_y = entity_y + box_height + spacing
    
    # Add identifiers
    for identifier in identifiers:
        items.append({
            'type': 'identifier',
            'name': identifier,
            'y': current_y,
            'has_dropdown': False
        })
        current_y += spacing
    
    # Add OOTB attributes
    for attr in attributes_ootb:
        items.append({
            'type': 'attribute',
            'name': attr,
            'y': current_y,
            'has_dropdown': attr in dropdown_fields
        })
        current_y += spacing
    
    # Add custom attributes
    for attr in attributes_custom:
        items.append({
            'type': 'attribute',
            'name': attr,
            'y': current_y,
            'has_dropdown': attr in dropdown_fields,
            'is_custom': True
        })
        current_y += spacing
    
    # Add field groups with their sub-fields
    for fg in field_groups:
        fg_name = fg['name']
        fg_type = fg.get('type', 'Custom')
        fg_ootb_fields = fg['fields'].get('ootb', [])
        fg_custom_fields = fg['fields'].get('custom', [])
        all_fg_fields = fg_ootb_fields + fg_custom_fields
        
        items.append({
            'type': 'field_group',
            'name': fg_name,
            'fg_type': fg_type,
            'y': current_y,
            'sub_fields': all_fg_fields,
            'has_dropdown': False
        })
        current_y += spacing
    
    # Calculate total height needed
    max_y = max([item['y'] for item in items]) if items else entity_y
    # Add space for field group sub-attributes
    for item in items:
        if item['type'] == 'field_group' and item['sub_fields']:
            max_y = max(max_y, item['y'] + len(item['sub_fields']) * spacing)
    
    svg_height = max(max_y + 100, 200)
    svg_width = 900  # Max width as specified
    
    # Build SVG
    svg_parts = [f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Title -->
  <text x="10" y="20" font-family="Arial" font-size="14" font-weight="bold" text-decoration="underline">
    {entity_name} Entity Hierarchy
  </text>
  
  <!-- Legend -->
  <rect x="10" y="30" width="780" height="40" fill="#f0f0f0" stroke="#666" stroke-width="1" rx="5"/>
  <text x="20" y="50" font-family="Arial" font-size="11" font-weight="bold">Legend:</text>
  <rect x="100" y="40" width="100" height="20" fill="#2196F3" stroke="#666" rx="3"/>
  <text x="105" y="53" font-family="Arial" font-size="9">Business Entity</text>
  <rect x="220" y="40" width="100" height="20" fill="#C5E1A5" stroke="#666" rx="3"/>
  <text x="225" y="53" font-family="Arial" font-size="9">General Attributes</text>
  <rect x="340" y="40" width="100" height="20" fill="#F8BBD9" stroke="#666" rx="3"/>
  <text x="345" y="53" font-family="Arial" font-size="9">Identifiers</text>
  <rect x="460" y="40" width="100" height="20" fill="#FFD54F" stroke="#666" rx="3"/>
  <text x="465" y="53" font-family="Arial" font-size="9">Field Groups</text>
  
  <!-- Main Entity Box (Blue) -->
  <rect x="{entity_x}" y="{entity_y}" width="{box_width}" height="{box_height}" fill="#2196F3" stroke="#666" stroke-width="1" rx="12"/>
  <text x="{trunk_x}" y="{entity_y + 18}" font-family="Arial" font-size="11" fill="white" text-anchor="middle" font-weight="bold">{entity_name}</text>
  
  <!-- Vertical trunk line from entity -->"""
    ]
    
    # Calculate trunk end position
    trunk_end_y = max([item['y'] for item in items]) if items else entity_y + box_height
    svg_parts.append(f'  <line x1="{trunk_x}" y1="{entity_y + box_height}" x2="{trunk_x}" y2="{trunk_end_y + box_height/2}" stroke="#666" stroke-width="1"/>\n')
    
    # Draw all items
    for item in items:
        item_center_x = col1_x + box_width / 2
        item_y = item['y']
        item_center_y = item_y + box_height / 2
        
        # Horizontal branch line from trunk to item
        svg_parts.append(f'  <line x1="{trunk_x}" y1="{item_center_y}" x2="{col1_x}" y2="{item_center_y}" stroke="#666" stroke-width="1"/>\n')
        
        if item['type'] == 'identifier':
            # Pink box for identifiers
            svg_parts.append(f'  <rect x="{col1_x}" y="{item_y}" width="{box_width}" height="{box_height}" fill="#F8BBD9" stroke="#666" stroke-width="1" rx="12"/>\n')
            svg_parts.append(f'  <text x="{item_center_x}" y="{item_y + 18}" font-family="Arial" font-size="10" text-anchor="middle">{item["name"]}</text>\n')
        
        elif item['type'] == 'attribute':
            # Green box for attributes
            display_name = item['name']
            if item.get('is_custom'):
                display_name += ' (custom)'
            svg_parts.append(f'  <rect x="{col1_x}" y="{item_y}" width="{box_width}" height="{box_height}" fill="#C5E1A5" stroke="#666" stroke-width="1" rx="12"/>\n')
            text_x = item_center_x
            if item['has_dropdown']:
                # Add dropdown indicator
                svg_parts.append(f'  <text x="{text_x}" y="{item_y + 18}" font-family="Arial" font-size="10" text-anchor="middle">{display_name}</text>\n')
                svg_parts.append(f'  <text x="{col1_x + box_width - 15}" y="{item_y + 12}" font-family="Arial" font-size="8" fill="#666">▼</text>\n')
            else:
                svg_parts.append(f'  <text x="{text_x}" y="{item_y + 18}" font-family="Arial" font-size="10" text-anchor="middle">{display_name}</text>\n')
        
        elif item['type'] == 'field_group':
            # Yellow box for field group
            fg_label = f"{item['name']} ({item['fg_type']})"
            svg_parts.append(f'  <rect x="{col1_x}" y="{item_y}" width="{box_width}" height="{box_height}" fill="#FFD54F" stroke="#666" stroke-width="1" rx="12"/>\n')
            svg_parts.append(f'  <text x="{item_center_x}" y="{item_y + 18}" font-family="Arial" font-size="10" text-anchor="middle">{fg_label}</text>\n')
            
            # Draw sub-fields in Column 2
            if item['sub_fields']:
                sub_y = item_y
                fg_right_x = col1_x + box_width
                fg_center_y = item_center_y
                # Add a small horizontal segment first, then branch to each sub-field
                branch_x = fg_right_x + 10  # Small gap before branching
                
                for sub_field in item['sub_fields']:
                    sub_center_x = col2_x + box_width / 2
                    sub_center_y = sub_y + box_height / 2
                    
                    # Draw line: from field group -> branch point -> sub-field
                    svg_parts.append(f'  <line x1="{fg_right_x}" y1="{fg_center_y}" x2="{branch_x}" y2="{fg_center_y}" stroke="#666" stroke-width="1"/>\n')
                    svg_parts.append(f'  <line x1="{branch_x}" y1="{fg_center_y}" x2="{branch_x}" y2="{sub_center_y}" stroke="#666" stroke-width="1"/>\n')
                    svg_parts.append(f'  <line x1="{branch_x}" y1="{sub_center_y}" x2="{col2_x}" y2="{sub_center_y}" stroke="#666" stroke-width="1"/>\n')
                    
                    # Green box for sub-field
                    svg_parts.append(f'  <rect x="{col2_x}" y="{sub_y}" width="{box_width}" height="{box_height}" fill="#C5E1A5" stroke="#666" stroke-width="1" rx="12"/>\n')
                    
                    # Check if sub-field has dropdown
                    if sub_field in dropdown_fields:
                        svg_parts.append(f'  <text x="{sub_center_x}" y="{sub_y + 18}" font-family="Arial" font-size="9" text-anchor="middle">{sub_field}</text>\n')
                        svg_parts.append(f'  <text x="{col2_x + box_width - 12}" y="{sub_y + 12}" font-family="Arial" font-size="7" fill="#666">▼</text>\n')
                    else:
                        svg_parts.append(f'  <text x="{sub_center_x}" y="{sub_y + 18}" font-family="Arial" font-size="9" text-anchor="middle">{sub_field}</text>\n')
                    
                    sub_y += spacing
    
    svg_parts.append('</svg>')
    
    svg_content = ''.join(svg_parts)
    
    with open(output_path, 'w') as f:
        f.write(svg_content)


def main():
    """Main execution orchestrator."""
    print("="*80)
    print("4-STEP MDM REQUIREMENTS PROCESSING")
    print("="*80)
    
    # Find Excel file
    excel_path = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        excel_file = find_excel_file(excel_path)
        print(f"\n📄 Input file: {excel_file}")
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    
    # Execute steps in sequence
    step_outputs = {}
    
    for step in STEP_WORKFLOW:
        print(f"\n▶️  Starting {step['description']} (Step {step['num']})...")
        
        # Validate input
        if not validate_step_input(step, step_outputs.get(step['num'] - 1)):
            print(f"\n❌ Execution stopped at Step {step['num']}")
            sys.exit(1)
        
        try:
            # Execute step
            if step['num'] == 1:
                step_output = step1_extract_requirements(excel_file)
            elif step['num'] == 2:
                step_output = step2_map_ootb_entities(step_outputs[1])
            elif step['num'] == 3:
                step_output = step3_design_data_model(step_outputs[2])
            elif step['num'] == 4:
                step_output = step4_create_diagrams(step_outputs[3])
            
            step_outputs[step['num']] = step_output
            
            # Save output path info
            if isinstance(step['output'], str) and step['output'] != 'excel_file':
                if step['output'].endswith('.json'):
                    print(f"  📝 Output: {OUTPUT_DIR / step['output']}")
                if step['output_md']:
                    print(f"  📝 Documentation: {OUTPUT_DIR / step['output_md']}")
        
        except Exception as e:
            print(f"\n❌ ERROR in Step {step['num']}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Summary
    print("\n" + "="*80)
    print("✅ ALL STEPS COMPLETE!")
    print("="*80)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for file in sorted(OUTPUT_DIR.rglob('*')):
        if file.is_file():
            print(f"  • {file.relative_to(OUTPUT_DIR.parent)}")


if __name__ == '__main__':
    main()

