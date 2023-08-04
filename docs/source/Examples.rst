Examples
========

Using `redonly` is straightforward. Here's a minimal example:

.. code-block:: python

   import redonly.redonly as ro
   ronly = ro.RedOnly('out_folder', ["subreddits", "to", "archive"])
   if not ronly.generate():
       print("Failure!")
   else:
       print("Success")


**RedOnly** has multiple options (see the details in the :doc:`Reference` page) for specifying language, style, etc.

Options can be specified like this:

.. code-block:: python

   import redonly.redonly as ro
   # Set the localization to french and the theme to dark
   opts = ro.Options(lang=ro.Language.fr, style=ro.Style.dark)
   ronly = ro.RedOnly('out_folder', ["subreddits", "to", "archive"], opts)
   if not ronly.generate():
       print("Failure!")
   else:
       print("Success")
