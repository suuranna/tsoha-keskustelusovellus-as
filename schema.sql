CREATE TABLE chains {
    id SERIAL PRIMARY KEY,
    topics_id INTEGER REFERENCES topics,
    user_id INTEGER REFERENCES users
    title TEXT,
    deleted BOOLEAN
};

CREATE TABLE topics {
    id SERIAL PRIMARY KEY,
    topic TEXT,
    public BOOLEAN,
    deleted BOOLEAN
};

CREATE TABLE messages {
    id SERIAL PRIMARY KEY,
    content TEXT,
    user_id INTEGER REFERENCES users,
    posting_date TIMESTAMP,
    begining BOOLEAN,
    chain_id INTEGER REFERENCES chains,
    deleted BOOLEAN
};

CREATE TABLE users {
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    admin BOOLEAN
};

CREATE TABLE private_topics_permissions {
    id SERIAL PRIMARY KEY,
    topics_id INTEGER REFERENCES topics,
    user_id INTEGER REFERENCES users
};

