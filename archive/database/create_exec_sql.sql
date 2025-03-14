-- Create the exec_sql function for executing dynamic SQL queries
CREATE OR REPLACE FUNCTION public.exec_sql(query text, params jsonb DEFAULT NULL)
RETURNS SETOF json AS $$
BEGIN
    IF params IS NULL THEN
        RETURN QUERY EXECUTE query;
    ELSE
        RETURN QUERY EXECUTE query USING params;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 