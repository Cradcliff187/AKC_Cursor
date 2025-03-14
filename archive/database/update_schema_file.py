#!/usr/bin/env python
"""
Schema File Updater

This script updates the supabase_schema.sql file with the missing tables
from schema_updates.sql to ensure the schema file is aligned with the database.
"""

import os
import re

def read_file(file_path):
    """Read a file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def write_file(file_path, content):
    """Write content to a file."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {str(e)}")
        return False

def extract_table_definitions(sql_content):
    """Extract table definitions from SQL content."""
    # Pattern to match CREATE TABLE statements
    pattern = r'CREATE TABLE IF NOT EXISTS public\.(\w+)\s*\(([\s\S]*?)\);'
    tables = {}
    
    matches = re.findall(pattern, sql_content)
    for table_name, columns_text in matches:
        tables[table_name] = f"CREATE TABLE public.{table_name} ({columns_text});"
    
    return tables

def update_schema_file(schema_file_path, updates_file_path):
    """Update the schema file with missing tables from the updates file."""
    # Read files
    schema_content = read_file(schema_file_path)
    updates_content = read_file(updates_file_path)
    
    if not schema_content or not updates_content:
        return False
    
    # Extract table definitions
    update_tables = extract_table_definitions(updates_content)
    
    # Check which tables are already in the schema file
    existing_tables = []
    for table_name in update_tables.keys():
        if f"CREATE TABLE public.{table_name}" in schema_content:
            existing_tables.append(table_name)
    
    # Remove existing tables from updates
    for table_name in existing_tables:
        del update_tables[table_name]
    
    if not update_tables:
        print("No new tables to add to the schema file.")
        return True
    
    # Find the position to insert new tables (after the last CREATE TABLE statement)
    last_table_pos = schema_content.rfind("CREATE TABLE public.")
    if last_table_pos == -1:
        print("Could not find any CREATE TABLE statements in the schema file.")
        return False
    
    # Find the end of the last table definition
    last_table_end = schema_content.find(");", last_table_pos)
    if last_table_end == -1:
        print("Could not find the end of the last table definition.")
        return False
    
    last_table_end += 2  # Include the ");
    
    # Insert new table definitions
    new_content = schema_content[:last_table_end] + "\n\n-- Added tables\n"
    for table_name, table_def in update_tables.items():
        new_content += f"\n{table_def}\n"
    new_content += schema_content[last_table_end:]
    
    # Write updated content back to the schema file
    if write_file(schema_file_path, new_content):
        print(f"Successfully added {len(update_tables)} new tables to the schema file:")
        for table_name in update_tables.keys():
            print(f"- {table_name}")
        return True
    else:
        return False

def main():
    """Main function."""
    schema_file_path = 'supabase_schema.sql'
    updates_file_path = 'schema_updates.sql'
    
    # Create backup of schema file
    backup_path = f"{schema_file_path}.bak"
    schema_content = read_file(schema_file_path)
    if schema_content:
        write_file(backup_path, schema_content)
        print(f"Created backup of schema file at {backup_path}")
    
    # Update schema file
    if update_schema_file(schema_file_path, updates_file_path):
        print("Schema file updated successfully.")
    else:
        print("Failed to update schema file.")

if __name__ == "__main__":
    main() 