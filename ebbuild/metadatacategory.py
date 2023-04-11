import tecoradors
from typing import Generic, List, Callable, TypeVar

T = TypeVar('T')
Result = TypeVar('Result')

Of = TypeVar('Of')


@tecoradors.stringable
class MetadataCategory(Generic[T, Result]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.was_set = False
        self.done = False
        self.result = None
        self.directive = '%{}'.format(self.name)

    def line_to_item_transform(self, item: str) -> T:
        '''
        Transforms a line of markdown text into a collection of metadata items in this category
        Generally this method is only called once per category on a line containing all the items for that category
        but it can be called many times if the same metadata directive (such as @tags) appears on many lines
        :param item:
        :return:
        '''
        raise NotImplementedError("Implement this method")

    def _extend_internal(self, item: T) -> None:
        self.was_set = True
        return self.extend(item)

    def extend(self, item: T) -> None:
        '''
        Method which extends the current collection of items to the collection of items for this particular category of metadata
        The collection may take any form and may contain 0 or more elements
        Generally this method is only called once per category on a line containing all the items for that category
        but it can be called many times if the same metadata directive (such as @tags) appears on many lines
        :param item: the new metadata item for this category
        :return: None
        '''
        raise NotImplementedError("Implement this method")

    def final_transform(self, collection: List[T]) -> Result:
        '''
        This method is used to take a collection of metadata items and perform a final processing step.
        This method is called after all lines of the file have been processed
        This method is useful for things like joining a list of items into a single str or similar
        :param collection: all the metadata items in this category
        :return: the result of the final transform
        '''
        raise NotImplementedError("Implement this method")

    def backing_collection(self) -> T:
        '''
        Gives access to the backing collection of this category
        :return: the category's backing collection
        '''
        raise NotImplementedError("Implement this method")

    def finalize(self):
        self.result = self.final_transform(self.backing_collection())
        self.done = True


    def __eq__(self, o: object) -> bool:
        return hasattr(o, 'name') and self.name == o.name

    def __ne__(self, o: object) -> bool:
        return not (self == o)

    def __str__(self) -> str:
        return 'Metadata<{1}>({0})'.format(repr(self.name), type(self.backing_collection()).__name__)

    def __hash__(self) -> int:
        return hash(self.name)


class BasicListMetadataFactory(MetadataCategory, Generic[Of]):

    def __init__(self, name: str, item_transform: Callable[[str], list[Of]]) -> None:
        super().__init__(name)
        self.contents = []
        self.item_transform = item_transform

    def line_to_item_transform(self, item: str) -> list[Of]:
        return self.item_transform(item)

    def extend(self, item: list[Of]) -> None:
        self.contents.extend(item)

    def final_transform(self, collection: List[List[Of]]) -> Result:
        return self.contents

    def backing_collection(self) -> list[Of]:
        return self.contents


class BasicStrMetadataFactory(MetadataCategory):

    def __init__(self, name: str, item_transform: Callable[[str], str]) -> None:
        super().__init__(name)
        self.contents = ''
        self.item_transform = item_transform

    def line_to_item_transform(self, item: str) -> str:
        return self.item_transform(item)

    def extend(self, item: str) -> None:
        self.contents += item

    def final_transform(self, collection: List[str]) -> Result:
        return self.contents

    def backing_collection(self) -> str:
        return self.contents


class BasicBoolMetadataFactory(MetadataCategory):
    def __init__(self, name: str, item_transform: Callable[[str], bool], init_value: bool = False) -> None:
        super().__init__(name)
        self.item_transform = item_transform
        self.initval = init_value
        self.contents = init_value

    def line_to_item_transform(self, item: str) -> bool:
        return self.item_transform(item)

    def extend(self, item: bool) -> None:
        self.contents = item

    def final_transform(self, collection: List[bool]) -> Result:
        return self.contents

    def backing_collection(self) -> bool:
        return self.contents
