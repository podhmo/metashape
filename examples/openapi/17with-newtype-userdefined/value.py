import typing as t


class Person:
    name: str


MyPerson = t.NewType("MyPerson", Person)
OptionalMyPerson2 = t.NewType("OptionalMyPerson", t.Optional[Person])
OptionalMyPerson3 = t.NewType("OptionalMyPerson2", t.Optional[MyPerson])

MyPeople = t.NewType("MyPeople", t.List[Person])
MyPeople2 = t.NewType("MyPeople2", t.List[MyPerson])
MyPeopleOptional = t.NewType("MyPeopleOptional", t.List[OptionalMyPerson2])


class Value:
    person: Person
    my_person: MyPerson

    optional_person: t.Optional[Person]
    optional_my_person: t.Optional[MyPerson]
    optional_my_person2: OptionalMyPerson2
    optional_my_person3: OptionalMyPerson3

    people: t.List[Person]
    my_people: MyPeople
    my_people2: MyPeople2
    my_people_optional: MyPeopleOptional

    optional_people: t.Optional[t.List[Person]]
    optional_my_people: t.Optional[MyPeople]
    optional_my_people2: t.Optional[MyPeople2]
