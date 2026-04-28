#!/usr/bin/env python3
import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from migration.service import (
    import_document,
    import_directory,
    list_documents,
    get_document_by_key,
    delete_document,
    clear_all_documents,
)


async def main():
    parser = argparse.ArgumentParser(description="Migration CLI for documents")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("init", help="Initialize database tables")
    
    import_parser = subparsers.add_parser("import-file", help="Import single file")
    import_parser.add_argument("file", help="Path to file")
    import_parser.add_argument("--no-update", action="store_true", help="Don't update existing documents")
    
    dir_parser = subparsers.add_parser("import-dir", help="Import directory")
    dir_parser.add_argument("directory", help="Path to directory")
    dir_parser.add_argument("--extensions", nargs="+", help="File extensions to import")
    dir_parser.add_argument("--no-update", action="store_true", help="Don't update existing documents")
    
    subparsers.add_parser("list", help="List all documents")
    
    get_parser = subparsers.add_parser("get", help="Get document by key")
    get_parser.add_argument("key", help="Document key")
    
    delete_parser = subparsers.add_parser("delete", help="Delete document by key")
    delete_parser.add_argument("key", help="Document key")
    
    subparsers.add_parser("clear", help="Clear all documents")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    match args.command:
        case "init":
            from api.database import create_db_and_tables
            await create_db_and_tables()
            print("Database initialized")
        
        case "import-file":
            result = await import_document(args.file, not args.no_update)
            print(f"Imported: {result.get('imported')}, Skipped: {result.get('skipped')}")
        
        case "import-dir":
            result = await import_directory(args.directory, args.extensions, not args.no_update)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Total imported: {result.get('total_imported')}, Skipped: {result.get('total_skipped')}")
        
        case "list":
            docs = await list_documents()
            for doc in docs:
                print(f"{doc['key']} - {doc['title']} ({doc['source_type']})")
        
        case "get":
            doc = await get_document_by_key(args.key)
            if doc:
                print(f"Key: {doc['key']}")
                print(f"Title: {doc['title']}")
                print(f"Text: {doc['text'][:200]}...")
            else:
                print("Document not found")
        
        case "delete":
            if await delete_document(args.key):
                print("Document deleted")
            else:
                print("Document not found")
        
        case "clear":
            count = await clear_all_documents()
            print(f"Cleared {count} documents")
        
        case _:
            parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())