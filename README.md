# Flexmoney-Assignment

ER Diagram Diagrammatic Representation
Here's a diagrammatic representation of the ER diagram for your fitness payment app:

      +-----------+       +------------+
      |   User    | ----> |   Payment   |
      +-----------+       +------------+
      | id        |       | id          |
      | username  |       | amount      |
      | email     |       | status      |
      | mobile    |       | created_at  |
      | age       |       | user_id      |
      | --------- |       | (fk)        |
      | preferred_ |       +------------+
      | batch_id   |
      +-----------+

      +-----------+
      |   Batch   |
      +-----------+
      | id        |
      | name      |
      +-----------+

      * User has one preferred Batch (one-to-one)
      * A Batch can have many Users with it as their preference (one-to-many)
      * User can have many Payments (one-to-many)
      * Payment belongs to one User (many-to-one)
Key:

Rectangles represent entities (User, Batch, Payment).
Diamonds represent relationships between entities.
Lines connect entities and relationships.
Attributes within each entity are listed below the entity name.
(fk) denotes a foreign key, referencing the primary key of another entity.
