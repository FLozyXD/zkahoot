create table if not exists lobbies (
       token text,
       name text,
       owner_id integer,
       quiz_id integer,
       running boolean,
       primary key (token)
);

create table if not exists lobbies_users (
       token text,
       user_id integer,
       foreign key (token) references lobbies(token)
)
