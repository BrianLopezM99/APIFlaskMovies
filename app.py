import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask import request

from flask_cors import CORS

app = Flask(__name__)
CORS(app)


GET_ACTORS = """SELECT * FROM actor"""

TOP_5_CUSTOMERS = """SELECT c.first_name, c.last_name, COUNT(*) as total_rentals
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY total_rentals DESC
LIMIT 5;
"""

TOP_5_FILMS = """SELECT f.title, COUNT(*) as total_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY f.film_id
ORDER BY total_rentals DESC
LIMIT 5;
"""

GET_INVENTORY = """SELECT film.film_id, film.title, film.release_year, film.rental_rate, inventory_id
FROM inventory
JOIN film ON inventory.film_id = film.film_id;
"""

GET_INVENTORY_BY_ID = """SELECT * FROM inventory WHERE inventory_id = %s"""

CREATE_INVENTORY = """INSERT INTO inventory (film_id, store_id) VALUES (%s, %s) RETURNING inventory_id"""

UPDATE_INVENTORY = """UPDATE inventory SET film_id = %s, store_id = %s WHERE inventory_id = %s"""

CREATE_FILM = """INSERT INTO film (title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating, special_features, fulltext)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

UPDATE_FILM = """
    UPDATE film SET title = %s, rental_rate = %s 
    WHERE film_id = (
        SELECT film_id FROM inventory WHERE inventory_id = %s
    )
"""

DELETE_FILM_ACTOR = """
                DELETE FROM film_actor WHERE film_id = %s
            """
DELETE_FILM_CATEGORY = """
                DELETE FROM film_category WHERE film_id = %s
            """


DELETE_FILM = """
                DELETE FROM film WHERE film_id = %s
            """

SELECT_RENTAL = """SELECT rental_id, rental_date
FROM rental
WHERE rental_id = %s;
"""

DELETE_PAYMENT = "DELETE FROM payment WHERE rental_id IN (SELECT rental_id FROM rental WHERE inventory_id = %s)"
DELETE_RENTAL = "DELETE FROM rental WHERE inventory_id = %s"
DELETE_INVENTORY = "DELETE FROM inventory WHERE inventory_id = %s"""

CREATE_FILM_CATEGORY = """INSERT INTO film_category VALUES(%s, %s);
"""

CREATE_FILM_ACTOR = """INSERT INTO film_actor VALUES (%s, %s);
"""


load_dotenv()

url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)


@app.get("/")
def home():
    return "Hello World"


@app.get("/api/top5customers")
def list():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_5_CUSTOMERS)
            rows = cursor.fetchall()

    print('resultado', rows)
   # Procesar los resultados y devolverlos como un diccionario
    results = []
    for row in rows:
        result = {
            "first_name": row[0],
            "last_name": row[1],
            "total_rentals": row[2]
        }
        results.append(result)

    return jsonify(results)


@app.get("/api/top5films")
def films():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_5_FILMS)
            rows = cursor.fetchall()

    print('resultado', rows)
   # Procesar los resultados y devolverlos como un diccionario
    results = []
    for row in rows:
        result = {
            "title": row[0],
            "total_rentals": row[1]
        }
        results.append(result)

    return {"films": results}


####################################################################

@app.route("/api/inventory", methods=["GET"])
def list_inventory():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_INVENTORY)
            rows = cursor.fetchall()

    results = []
    for row in rows:
        result = {
            "film_id": row[0],
            "title": row[1],
            "release_year": row[2],
            "rental_rate": row[3],
            "inventory_id": row[4]
        }
        results.append(result)

    return {"inventory": results}


@app.route("/api/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_INVENTORY_BY_ID, (inventory_id,))
            row = cursor.fetchone()

    if row:
        result = {
            "inventory_id": row[0],
            "film_id": row[1],
            "store_id": row[2],
            "last_update": row[3]
        }
        return result
    else:
        return {"error": "Inventory not found"}


@app.route('/api/films', methods=['POST'])
def create_film():
    data = request.json
    title = data['title']
    description = data['description']
    release_year = data['release_year']
    language_id = data['language_id']
    rental_duration = data['rental_duration']
    rental_rate = data['rental_rate']
    length = data['length']
    replacement_cost = data['replacement_cost']
    rating = data['rating']
    special_features = data['special_features']
    fulltext = data['fulltext']
    category_id = data['category_id']
    store_id = data['store_id']

    # Ejecuta la consulta SQL usando la conexión a la base de datos
    with connection:
        with connection.cursor() as cursor:
            # Crea la película
            cursor.execute(CREATE_FILM, (title, description, release_year, language_id, rental_duration,
                                         rental_rate, length, replacement_cost, rating, special_features, fulltext))
        
            cursor.execute("SELECT film_id FROM film WHERE title = %s AND release_year = %s", (title, release_year))
            new_film = cursor.fetchone()
            new_film_id = new_film[0]

            # Ejecuta la consulta SQL para obtener el inventory_id de la última fila insertada
            cursor.execute("SELECT inventory_id FROM inventory ORDER BY inventory_id DESC LIMIT 1;")
            last_inventory_id = cursor.fetchone()[0]
            new_inventory_id = last_inventory_id + 1


            cursor.execute("INSERT INTO film_category VALUES (%s, %s)", (new_film_id, category_id))
            cursor.execute("INSERT INTO inventory VALUES (%s, %s, %s)", (new_inventory_id, new_film_id, store_id))


    # Devuelve una respuesta con un mensaje de éxito
    return {'message': f'Película creada exitosamente ${new_film_id}'}, 201



@app.put("/api/film/<int:film_id>")
def update_film(film_id):
    # Obtener los nuevos valores del cuerpo de la petición
    new_title = request.json.get('title')
    new_rate = request.json.get('rate')


    with connection:
        with connection.cursor() as cursor:
            # Actualizar los valores en la tabla
            cursor.execute(UPDATE_FILM, (new_title, new_rate, film_id))

    # Devolver una respuesta exitosa
    return {"message": "Película actualizada correctamente"}


@app.route("/api/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    data = request.json
    film_id = data["film_id"]
    store_id = data["store_id"]

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_INVENTORY, (film_id, store_id, inventory_id))
            connection.commit()

    result = {
        "inventory_id": inventory_id,
        "film_id": film_id,
        "store_id": store_id
    }

    return result


@app.delete("/api/inventory/<int:inventory_id>")
def delete_inventory(inventory_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_PAYMENT, (inventory_id,))
            cursor.execute(DELETE_RENTAL, (inventory_id,))
            cursor.execute(DELETE_INVENTORY, (inventory_id,))
            
    # Devolver una respuesta exitosa
    return {"message": "Inventario eliminado correctamente"}


if __name__ == '__main__':
    app.run()

# {
#   "title": "Pelicula de prueba",
#   "description": "descripcion de prueba",
#   "release_year": 2002,
#   "language_id": 2,
# "rental_duration": 2000,
# "rental_rate": 3,
# "length": 129,
# "replacement_cost": 12,
# "rating": "G",
# "special_features": "textxd",
# "fulltext": "Esto es un texto de prueba"
# }
