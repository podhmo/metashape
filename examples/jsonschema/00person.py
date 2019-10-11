import metashape


@metashape.mark
class Person:
    name: str
    age: int


# main
print(
    metashape.translate(
        metashape.Accessor(
            resolver=metashape.FakeResolver(), repository=metashape.FakeRepository([Person])
        )
    )
)
