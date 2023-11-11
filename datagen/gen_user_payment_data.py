import psycopg2
import argparse
from time import sleep
import random
from faker import Faker

fake = Faker()


def get_key_for_gen_data() -> int:
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            "dbname='postgres' user='postgres' host='postgres_custom' password='postgres'"
        )

        # Create a cursor
        curr = conn.cursor()

        # Execute the SQL query to get the count of records in the users table
        curr.execute("SELECT count(*) FROM commerce.users")

        # Fetch the result
        count = curr.fetchone()[0]

        # Close the cursor and the connection
        curr.close()
        conn.close()

        # Return the count
        return count

    except Exception as e:
        print(f"Error: {e}")
        return 0  # Return 1 to indicate an error


def gen_data(num_records: int) -> None:
    # how to handel if connection refuse
    start = get_key_for_gen_data()
    for id in range(start+1, num_records):
        sleep(1)
        conn = psycopg2.connect(
            "dbname='postgres' user='postgres' host='postgres_custom' password='postgres'"
        )
        curr = conn.cursor()
        curr.execute(
            "INSERT INTO commerce.users (id, username, password) VALUES (%s, %s, %s)",
            (id, fake.user_name(), fake.password()),
        )
        curr.execute(
            "INSERT INTO commerce.products (id, name, description, price) VALUES (%s, %s, %s, %s)",
            (id, fake.name(), fake.text(), fake.random_int(min=1, max=100)),
        )
        curr.execute(
            "INSERT INTO commerce.orders (id, user_id, product_id, quantity, order_date) VALUES (%s, %s, %s, %s, %s)",
            (id, id, id, fake.random_int(min=1, max=10), fake.date_this_month()),
        )
        conn.commit()

        sleep(0.5)
        # update 10 % of the time
        if random.randint(1, 100) >= 90:
            curr.execute(
                "UPDATE commerce.users SET username = %s WHERE id = %s",
                (fake.user_name(), id),
            )
            curr.execute(
                "UPDATE commerce.products SET name = %s WHERE id = %s",
                (fake.name(), id),
            )
        conn.commit()

        # sleep(0.5)
        # # delete 5 % of the time
        # if random.randint(1, 100) >= 95:
        #     curr.execute("DELETE FROM commerce.users WHERE id = %s", (id,))
        #     curr.execute("DELETE FROM commerce.products WHERE id = %s", (id,))

        conn.commit()
        curr.close()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--num_records",
        type=int,
        help="Number of records to generate",
        default=1000,
    )
    args = parser.parse_args()
    num_records = args.num_records
    gen_data(num_records)
