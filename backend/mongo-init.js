db = db.getSiblingDB('pramaan_shield');

db.createUser({
  user: "pramaan_app",
  pwd: process.env.MONGO_APP_PASSWORD || "change_me_in_env",
  roles: [
    {
      role: "readWrite",
      db: "pramaan_shield"
    }
  ]
});

db.createCollection("sebi_registry");
db.createCollection("seal_records");
db.createCollection("scan_history");
db.createCollection("flagged_content");
db.createCollection("user_reports");
db.createCollection("audit_ledger");

print("MongoDB initialized — pramaan_shield database and app user created");
