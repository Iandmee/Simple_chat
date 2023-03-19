# :envelope::envelope::envelope: Console_chat :envelope::envelope::envelope:
## Server initialization
With *Gunicorn* in *server* folder: <br>
```gunicorn -w 5 wsgi:app``` <br>
Without *Gunicorn*: <br>
```python3 run_server.py ``` <br>
## Client usage
Just run: <br>
```python3 client.py ``` <br>
### Chat options
To exit from chat use ```#exit```
