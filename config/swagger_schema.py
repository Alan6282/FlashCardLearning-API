from drf_yasg.generators import OpenAPISchemaGenerator

class OrderedSchemaGenerator(OpenAPISchemaGenerator):
    """
    Custom schema generator that preserves tag order
    and adds tag descriptions for drf_yasg.
    """

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)

        schema.tags = [
            {
                "name": "Authentication",
                "description": "Endpoints for user registration, login, logout, and token refresh."
            },
            {
                "name": "FlashCard-Decks",
                "description": "APIs for listing decks, viewing details, and managing associated cards."
            },
            {
                "name": "FlashCard-Cards",
                "description": "Operations related to flashcards — create, list, retrieve, update, and delete cards."
            },
            {
                "name": "FlashCard-Reviews",
                "description": "Endpoints for creating and retrieving flashcard reviews for each card."
            },
          
           {
                "name": "FlashCard-Stats",
                "description": (
                    "Endpoints that provide learning statistics at both deck and user levels — including "
                    "total card counts, progress, due/overdue cards, performance metrics, and mastered cards."
                )
           },
           {
                "name": "FlashCard-Suggestions",
                "description": (
                    "Endpoints that generate personalized study recommendations — including deck-specific "
                    "suggestions and global review suggestions across all flashcards."
                )
            },
        ]

        return schema