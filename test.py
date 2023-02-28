import Connect

with Connect.Connect() as conn:
    sql = "select * from task_list"
    task_list = conn.fetch_all(sql)
    print(task_list)