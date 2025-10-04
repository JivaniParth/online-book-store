#!/usr/bin/env python3
"""
MySQL Database Setup Script for BookHaven
This script verifies your MySQL connection and ensures tables exist
"""

import sys
import pymysql
from app import create_app
from database import db


def test_mysql_connection():
    """Test if MySQL connection is working"""
    print("\n" + "=" * 60)
    print("TESTING MYSQL CONNECTION")
    print("=" * 60)

    app = create_app()

    # Print connection details (hide password)
    from config import Config

    print(f"\nConnection Details:")
    print(f"  Host: {Config.MYSQL_HOST}")
    print(f"  Port: {Config.MYSQL_PORT}")
    print(f"  User: {Config.MYSQL_USER}")
    print(f"  Database: {Config.MYSQL_DATABASE}")
    print(f"  Password: {'*' * len(Config.MYSQL_PASSWORD)}")

    try:
        # Test basic connection
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
        )
        print("\n✅ Successfully connected to MySQL!")

        # Test if tables exist
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print(f"\n📋 Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        connection.close()

        return True

    except pymysql.Error as e:
        print(f"\n❌ MySQL Connection Error: {e}")
        print("\nTroubleshooting Tips:")
        print("  1. Make sure MySQL is running")
        print("  2. Check your credentials in .env file")
        print("  3. Ensure 'bookstore' database exists")
        print(
            "  4. Grant permissions: GRANT ALL PRIVILEGES ON bookstore.* TO 'root'@'localhost';"
        )
        return False


def verify_tables():
    """Verify all required tables exist"""
    print("\n" + "=" * 60)
    print("VERIFYING DATABASE TABLES")
    print("=" * 60)

    app = create_app()

    required_tables = [
        "User",
        "Publisher",
        "Category",
        "Author",
        "Book_Details",
        "Cart",
        "Book_Order",
        "Order_Item",
        "Review",
    ]

    try:
        with app.app_context():
            # Get existing tables
            result = db.engine.execute("SHOW TABLES")
            existing_tables = [row[0] for row in result]

            print(f"\nChecking for required tables...")
            missing_tables = []

            for table in required_tables:
                if table in existing_tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - MISSING")
                    missing_tables.append(table)

            if missing_tables:
                print(f"\n⚠️  Missing {len(missing_tables)} table(s)")
                print(
                    "\nPlease run your DDL script (final relations.txt) in MySQL to create tables:"
                )
                print("  mysql -u root -p bookstore < final_relations.txt")
                return False
            else:
                print(f"\n✅ All {len(required_tables)} required tables exist!")
                return True

    except Exception as e:
        print(f"\n❌ Error verifying tables: {e}")
        return False


def check_sample_data():
    """Check if database has sample data"""
    print("\n" + "=" * 60)
    print("CHECKING SAMPLE DATA")
    print("=" * 60)

    app = create_app()

    try:
        with app.app_context():
            from models.user import User
            from models.book import Book
            from models.category import Category

            user_count = User.query.count()
            book_count = Book.query.count()
            category_count = Category.query.count()

            print(f"\nCurrent data:")
            print(f"  Users: {user_count}")
            print(f"  Books: {book_count}")
            print(f"  Categories: {category_count}")

            if user_count == 0 and book_count == 0 and category_count == 0:
                print("\n⚠️  Database is empty. You may want to add sample data.")
                return False
            else:
                print("\n✅ Database contains data!")
                return True

    except Exception as e:
        print(f"\n❌ Error checking data: {e}")
        return False


def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("BOOKHAVEN - MYSQL DATABASE SETUP")
    print("=" * 60)

    # Step 1: Test MySQL connection
    if not test_mysql_connection():
        print("\n❌ Setup failed at connection test")
        sys.exit(1)

    # Step 2: Verify tables
    if not verify_tables():
        print("\n❌ Setup failed at table verification")
        print("\nNext steps:")
        print("  1. Make sure you've run your DDL script")
        print("  2. Run: mysql -u root -p bookstore < final_relations.txt")
        sys.exit(1)

    # Step 3: Check sample data
    check_sample_data()

    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nYour Flask app is ready to connect to MySQL.")
    print("You can now start the server with: python app.py")
    print("\nIf you need to add sample data, you can:")
    print("  1. Insert data manually in MySQL")
    print("  2. Use the Flask app to register users and add books")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
