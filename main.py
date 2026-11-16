
import time
import random
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
from colorama import init, Fore, Style

init(autoreset=True)


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="shark_user",
        password=os.getenv("DB_PASSWORD"),
        database="miss_shark"
    )


def setup_database():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cases (
            case_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            answer VARCHAR(100) NOT NULL,
            difficulty VARCHAR(20),
            case_date VARCHAR(20)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM Cases")
    count = cursor.fetchone()[0]

    if count == 0:
        cases = [
            ("The Missing Necklace",
             "A necklace disappeared during a party. The only people nearby were Mia, Sam and Alex.",
             "mia", "Easy", "2026-01-01"),

            ("The Broken Window",
             "A classroom window broke during lunch. Ravi says he was in the library.",
             "ravi", "Medium", "2026-01-02"),

            ("The Vanishing Cupcake",
             "A cupcake vanished from the kitchen. Lily had frosting on her fingers.",
             "lily", "Easy", "2026-01-03"),

            ("The Secret Letter",
             "A secret letter disappeared from the desk. Noah was the last person seen there.",
             "noah", "Medium", "2026-01-04"),

            ("The Missing Trophy",
             "The school trophy went missing. Emma was responsible for cleaning the display room.",
             "emma", "Hard", "2026-01-05")
        ]

        cursor.executemany("""
            INSERT INTO Cases
            (title, description, answer, difficulty, case_date)
            VALUES (%s, %s, %s, %s, %s)
        """, cases)

    connection.commit()
    cursor.close()
    connection.close()


def welcome_screen():
    print("\n")
    print(Fore.LIGHTMAGENTA_EX + "╭────────────────────────────────────╮")
    print(Fore.LIGHTMAGENTA_EX + "          MISS SHARK'S")
    print(Fore.LIGHTMAGENTA_EX + "          MYSTERY FILES")
    print(Fore.LIGHTMAGENTA_EX + "╰────────────────────────────────────╯")
    print(Fore.MAGENTA + "\n       Every Clue Tells a Story!")
    print("\n       Welcome, Detective!")
    print("\n       Preparing your mystery", end="", flush=True)

    for i in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)

    print("\n\n       Your next case awaits!")
    input("\n       Press Enter to continue...")


def display_cases():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT case_id, title, description, difficulty
        FROM Cases ORDER BY case_id
    """)
    cases = cursor.fetchall()

    print(Fore.LIGHTMAGENTA_EX + "\n--- MYSTERY CASES ---")

    if not cases:
        print("No cases found.")
    else:
        for case in cases:
            print(f"\nCase ID: {case[0]}")
            print(f"Title: {case[1]}")
            print(f"Description: {case[2]}")
            print(f"Difficulty: {case[3]}")
            print("-" * 35)

    cursor.close()
    connection.close()


def play_game():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT case_id, title, description, answer, difficulty FROM Cases")
    cases = cursor.fetchall()

    cursor.close()
    connection.close()

    if not cases:
        print("No mysteries available. Add a case first!")
        return

    case = random.choice(cases)

    print(Fore.LIGHTMAGENTA_EX + "\n--- DETECTIVE CHALLENGE ---")
    print("Case:", case[1])
    print("Difficulty:", case[4])
    print("Clue:", case[2])

    guess = input("\nWho do you suspect? ").strip()

    if guess.lower() == case[3].strip().lower():
        print(Fore.GREEN + "Correct! Amazing detective work!")
    else:
        print(Fore.YELLOW + "Not quite, detective!")
        print("The answer was:", case[3])


def add_case():
    title = input("Enter case title: ").strip()
    description = input("Enter case description: ").strip()
    answer = input("Enter the correct answer: ").strip()
    difficulty = input("Enter difficulty (Easy/Medium/Hard): ").strip()

    if not title or not description or not answer:
        print("Title, description and answer cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Cases (title, description, answer, difficulty)
        VALUES (%s, %s, %s, %s)
    """, (title, description, answer, difficulty))

    connection.commit()
    cursor.close()
    connection.close()

    print(Fore.GREEN + "Mystery case added successfully!")


def search_case():
    keyword = input("Enter a case title or keyword: ").strip()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT case_id, title, description, difficulty
        FROM Cases
        WHERE title LIKE %s OR description LIKE %s
    """, (f"%{keyword}%", f"%{keyword}%"))

    cases = cursor.fetchall()

    if cases:
        for case in cases:
            print(f"\nCase ID: {case[0]}")
            print(f"Title: {case[1]}")
            print(f"Description: {case[2]}")
            print(f"Difficulty: {case[3]}")
    else:
        print("No matching cases found.")

    cursor.close()
    connection.close()


def update_case():
    display_cases()

    try:
        case_id = int(input("\nEnter the Case ID to update: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    print("\n1. Update title")
    print("2. Update description")
    print("3. Update answer")
    print("4. Update difficulty")

    choice = input("Choose what to update (1-4): ").strip()

    columns = {
        "1": ("title", "Enter the new title: "),
        "2": ("description", "Enter the new description: "),
        "3": ("answer", "Enter the new answer: "),
        "4": ("difficulty", "Enter the new difficulty: ")
    }

    if choice not in columns:
        print("Invalid choice.")
        return

    column, prompt = columns[choice]
    value = input(prompt).strip()

    if not value:
        print("The new value cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        f"UPDATE Cases SET {column} = %s WHERE case_id = %s",
        (value, case_id)
    )

    connection.commit()

    if cursor.rowcount:
        print(Fore.GREEN + "Case updated successfully!")
    else:
        print("Case ID not found.")

    cursor.close()
    connection.close()


def delete_case():
    display_cases()

    try:
        case_id = int(input("\nEnter the Case ID to delete: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    confirm = input("Are you sure? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Deletion cancelled.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Cases WHERE case_id = %s", (case_id,))
    connection.commit()

    if cursor.rowcount:
        print(Fore.GREEN + "Case deleted successfully!")
    else:
        print("Case ID not found.")

    cursor.close()
    connection.close()


def main():
    try:
        welcome_screen()
        setup_database()

        while True:
            print("\n")
            print(Fore.LIGHTMAGENTA_EX + "╭────── MISS SHARK'S ──────╮")
            print(Fore.LIGHTMAGENTA_EX + "        MYSTERY FILES")
            print(Fore.LIGHTMAGENTA_EX + "╰─────────────────────────╯")
            print(Fore.MAGENTA + "1. Play a mystery")
            print(Fore.MAGENTA + "2. Display all cases")
            print(Fore.MAGENTA + "3. Add a case")
            print(Fore.MAGENTA + "4. Search for a case")
            print(Fore.MAGENTA + "5. Update a case")
            print(Fore.MAGENTA + "6. Delete a case")
            print(Fore.MAGENTA + "7. Exit")

            choice = input("\nEnter your choice (1-7): ").strip()

            try:
                if choice == "1":
                    play_game()
                elif choice == "2":
                    display_cases()
                elif choice == "3":
                    add_case()
                elif choice == "4":
                    search_case()
                elif choice == "5":
                    update_case()
                elif choice == "6":
                    delete_case()
                elif choice == "7":
                    print("Thanks for playing, detective! Bye!")
                    break
                else:
                    print("Invalid choice. Enter a number from 1 to 7.")

            except mysql.connector.Error as error:
                print("Database error:", error)

    except mysql.connector.Error as error:
        print("Could not connect to MySQL:", error)
        print("Check the MySQL username, password and database.")

    except (KeyboardInterrupt, EOFError):
        print("\nGame closed. Goodbye!")


if __name__ == "__main__":
    main()

