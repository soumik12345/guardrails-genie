from fasthtml.components import Div, A, Ul, Li, Details, Summary


def SafeGuardsNavBar():
    return Div(
        Div(
            A("SafeGuards", cls='btn btn-ghost text-xl'),
            cls='flex-1'
        ),
        Div(
            Ul(
                Li(
                    Details(
                        Summary("GuardRails"),
                        Ul(
                            Li(A("Playground", href="#")),
                            Li(A("Evaluation", href="#")),
                            cls='bg-base-100 rounded-t-none p-2'
                        )
                    )
                ),
                Li(A("Settings", href="#")),
                cls='menu menu-horizontal px-1'
            ),
            cls='flex-none'
        ),
        cls='navbar bg-base-100'
    )
