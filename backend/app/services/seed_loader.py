import asyncio
import json
import os
from sqlalchemy import select
from app.database import SessionLocal, engine, Base
from app.models import Ruleset, Rule
from datetime import datetime
import hashlib

# Define the path to the seeds directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # backend/app/services -> backend
# Actually simpler: assume run from backend root
# Or use absolute path logic relative to this file
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "db", "seeds")
# But our structure is pei/db/seeds and pei/backend with this file in pei/backend/app/services
# So we need to go up: services -> app -> backend -> pei -> db/seeds
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SEEDS_DIR = os.path.join(PROJECT_ROOT, "db", "seeds")

async def load_seeds():
    async with SessionLocal() as db:
        # Create default ruleset from multiple files
        seed_files = [
            "isa_letter_codes.json",
            "equipment_classes.json",
            "validation_rules.json",
            "generation_rules.json"
        ]
        
        rules_data = []
        for filename in seed_files:
            file_path = os.path.join(SEEDS_DIR, filename)
            if not os.path.exists(file_path):
                print(f"Warning: No {filename} found at {file_path}")
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    rules_data.extend(data)
                else:
                    print(f"Warning: {filename} does not contain a JSON array. Skipping.")
                    
        if not rules_data:
            print("No rules data loaded from seed files.")
            return
        
        # Calculate hash of the content
        rules_json_str = json.dumps(rules_data, sort_keys=True)
        ruleset_hash = hashlib.sha256(rules_json_str.encode()).hexdigest()
        
        ruleset_name = "pei-default"
        ruleset_version = 1
        
        # Check if ruleset exists
        stmt = select(Ruleset).where(Ruleset.name == ruleset_name, Ruleset.version == ruleset_version)
        result = await db.execute(stmt)
        existing_ruleset = result.scalar_one_or_none()
        
        if existing_ruleset:
            print(f"Ruleset {ruleset_name} v{ruleset_version} already exists.")
            return

        print(f"Creating Ruleset {ruleset_name} v{ruleset_version}...")
        ruleset = Ruleset(
            name=ruleset_name,
            version=ruleset_version,
            hash=ruleset_hash,
            description="Initial default ruleset from PEI documentation",
            status="active"
        )
        db.add(ruleset)
        await db.flush() # get ID

        for r_data in rules_data:
            rule = Rule(
                ruleset_id=ruleset.id,
                code=r_data.get("code", "UNKNOWN_CODE"),
                category=r_data.get("category", "general"),
                kind=r_data.get("kind", "reference"),
                scope=r_data.get("scope", "both"),
                severity=r_data.get("severity"),
                name_ko=r_data.get("name_ko", r_data.get("equipment_class_ko", r_data.get("variable_ko", ""))),
                name_en=r_data.get("name_en", r_data.get("equipment_class", r_data.get("variable", ""))),
                description=r_data.get("description", r_data.get("examples", "")),
                condition_json=r_data.get("condition_json"),
                action_json=r_data.get("action_json"),
                message_template=r_data.get("message_template"),
                reference=r_data.get("reference"),
                layer=r_data.get("layer", "L3"),
                priority=r_data.get("priority", 100),
                is_overridable=r_data.get("is_overridable", True),
                enabled=r_data.get("enabled", True)
            )
            db.add(rule)
        
        await db.commit()
        print("Seed data loaded successfully.")

if __name__ == "__main__":
    asyncio.run(load_seeds())
