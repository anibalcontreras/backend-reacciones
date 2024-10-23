# Instrucciones Generales

1. Requisitos: Tener instalado python. Se procede con la creación de un ambiente virtual, que se hace con los comandos a continuación

2. Comandos

```
pipenv install
```

```
pipenv shell
```

```
python manage.py makemigrations
```

```
python manage.py migrate

```

```
python manage.py loaddata users/fixtures/default_users.json
```

```
python manage.py loaddata services/fixtures/default_services.json

```

```
python manage.py runserver
```

3. Ya con esto, se tiene cargada una seed data con solicitantes, proveedores y recipients, además de los servicios charchazo y abrazo. Estos son los datos para iniciar sesión:

```
email: solicitor123@dummymail.com
password: charchazopalquelee
```

```
email: proveedor456@dummymail.com
password: rayomcqueen
```

4. Ahora se tiene que dirigr a el repositorio _frontend-reactions_ para levantar el frontend y con eso se podrá disfrutar del MVP.

Extra: Cualquier problema, no dude en contactarse conmigo al correo: anibal.conteras@uc.cl
