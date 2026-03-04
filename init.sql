create schema a_mongo_ass;

create type a_mongo_ass.status as enum ('created', 'deleted');

create table a_mongo_ass.deployments(
    id UUID PRIMARY KEY default (uuidv7()),
    db_name VARCHAR not null,
    status a_mongo_ass.status not null,
    username VARCHAR not null,
    creation_time timestamp without time zone not null default (current_timestamp at time zone 'utc')
);