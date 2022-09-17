# DRCTask

Please follow below steps:-

1. Install Virtual environemnt 
    1. virtualenv venv
2. activate virtual environment
    1. source venv/bin/activate
3. Install dependicies.
  1. pip3 install -r requirements.txt
4. Run migrations as mentioned in the order
   1. python3 manage.py makemigrations accounts
   2. python3 manage.py migrate accounts
   3. python3 manage.py makemigrations accounts
   4. python3 manage.py migrate accounts

5 Run following api's
   
  1. http://127.0.0.0.1:8000/api/v1/add-user 
    payload= {
    "first_name":"Naveen",
    "last_name":"Chaudhary",
    "primary_email":"deepak@gmail.com",
    "password":"qwerty123",
    "username":"Naveen13",
    "mobile":"8130481915"
    
}

  2.  API to send otp to mobile
     url :- http:// 127.0.0.1/api/v1/send-otp
     payload =
              {"mobile":"8130481915"}
              
  response= {
    "status": true,
    "code": 200,
    "message": "Success",
    "data": {
        "id": 20,
        "otp": "5254",
        "count": 0,
        "created_at": "2022-09-17T16:54:33.067965Z",
        "user": 4
    }
}

  3. API to Verify otp
          url :- http:// 127.0.0.1/api/v1/send-otp
    payload= {
              "mobile":"8130481915",
              "otp":"1826
}
}

    response={
    "status": true,
    "code": 200,
    "message": "Success",
    "data": {
        "message": "success",
        "token": "70ab1b07ea1c4560809c358c0eb77996220ea2f0"
    }
}
}

   
     
   

   
