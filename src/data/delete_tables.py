from src.data.sql_exec import SqlExec

if __name__ == '__main__':
    sql_exec = SqlExec()

    tables = sql_exec.inspector.get_table_names()
    tables.remove('spatial_ref_sys')
    table_str = ', '.join(tables)
    import ipdb; ipdb.set_trace()

    with sql_exec.engine.connect() as conn:
        conn.execute(f'DROP TABLE {table_str};')