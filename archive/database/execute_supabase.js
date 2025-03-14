// Execute SQL using Supabase JavaScript client
require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const fetch = require('node-fetch');

// Get environment variables
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

console.log(`SUPABASE_URL: ${SUPABASE_URL}`);
console.log(`SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY ? 'Set (length: ' + SUPABASE_SERVICE_KEY.length + ')' : 'Not set'}`);

// Create Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Check if file path is provided
if (process.argv.length < 3) {
  console.error('Usage: node execute_supabase.js <sql_file>');
  process.exit(1);
}

const filePath = process.argv[2];
console.log(`File path: ${filePath}`);

// Check if file exists
if (!fs.existsSync(filePath)) {
  console.error(`Error: File ${filePath} does not exist.`);
  process.exit(1);
}

// Read SQL file
const sqlContent = fs.readFileSync(filePath, 'utf8');
console.log(`SQL content length: ${sqlContent.length}`);

// Split SQL into statements
const statements = sqlContent.split(';').filter(stmt => stmt.trim() !== '');
console.log(`Number of SQL statements: ${statements.length}`);

// Execute SQL statements
async function executeSQL() {
  let successCount = 0;
  let errorCount = 0;

  for (const statement of statements) {
    try {
      console.log(`Executing SQL statement: ${statement.trim().substring(0, 100)}...`);
      
      // Execute SQL statement
      const { data, error } = await supabase.rpc('exec_sql', { query: statement.trim() });
      
      if (error) {
        console.error(`Error executing SQL statement: ${error.message}`);
        console.error(`Statement: ${statement.trim()}`);
        errorCount++;
      } else {
        console.log('SQL executed successfully.');
        successCount++;
      }
    } catch (e) {
      console.error(`Exception executing SQL statement: ${e.message}`);
      console.error(`Statement: ${statement.trim()}`);
      errorCount++;
    }
  }

  console.log(`SQL file execution completed: ${successCount} statements succeeded, ${errorCount} statements failed.`);
  return errorCount === 0;
}

// Create exec_sql function if it doesn't exist
async function createExecSQLFunction() {
  try {
    console.log('Creating exec_sql function...');
    
    const sql = `
    CREATE OR REPLACE FUNCTION public.exec_sql(query text) 
    RETURNS SETOF json AS $$
    BEGIN
        RETURN QUERY EXECUTE query;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    `;
    
    // Try creating it using the REST API first
    console.log('Attempting to create exec_sql function using REST API...');
    
    try {
      const response = await fetch(`${SUPABASE_URL}/rest/v1/sql`, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_SERVICE_KEY,
          'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({ query: sql })
      });
      
      console.log(`REST API response status: ${response.status}`);
      
      if (response.ok) {
        console.log('exec_sql function created successfully using REST API.');
        return true;
      } else {
        const responseText = await response.text();
        console.error(`Error creating exec_sql function using REST API: ${response.status}`);
        console.error(`Response: ${responseText}`);
      }
    } catch (e) {
      console.error(`Exception creating exec_sql function using REST API: ${e.message}`);
    }
    
    // Try using the RPC method
    console.log('Attempting to create exec_sql function using RPC method...');
    
    const { data, error } = await supabase.rpc('exec_sql', { query: sql });
    
    if (error) {
      console.error(`Error creating exec_sql function using RPC: ${error.message}`);
      return false;
    } else {
      console.log('exec_sql function created successfully using RPC.');
      return true;
    }
  } catch (e) {
    console.error(`Exception creating exec_sql function: ${e.message}`);
    return false;
  }
}

// Main function
async function main() {
  try {
    console.log('Starting execution...');
    
    // Create exec_sql function
    const execSqlCreated = await createExecSQLFunction();
    console.log(`exec_sql function created: ${execSqlCreated}`);
    
    // Execute SQL file
    const success = await executeSQL();
    
    process.exit(success ? 0 : 1);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

main(); 