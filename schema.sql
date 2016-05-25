drop table if exists tests;
create table tests (
  id integer primary key autoincrement,
  title text not null,
  description text not null,
  vector text not null,
  status text not null,
  impact integer,
  confidence integer,
  ease integer
);
