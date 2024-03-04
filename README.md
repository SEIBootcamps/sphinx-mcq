# sphinx-mcq

> Sphinx extension for building multiple choice questions.

## Usage

```rst
.. mcq:: Write your question statement here.
   :numbered:
   :answer: B

   You can add additional text for the prompt too.

   A. Answer one

      :feedback: Use this field list syntax to explain why this answer is
                 right/wrong.

   B. Answer two

      :feedback: Use this field list syntax to explain why this answer is
                 right/wrong.

   C. Answer three

      :feedback: Use this field list syntax to explain why this answer is
                 right/wrong.
```

### Options

| Name          | Type           | Description                                                                                                                                                                    |
| ------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| answer        | `unchanged`    | The correct answer (ex.: `A`, `B`, `C`...)                                                                                                                                     |
| class         | `class_option` | List of space-separated class names to add to the node.                                                                                                                        |
| name          | `unchanged`    | Use this option to specify a DOM ID for the node. It will be prefixed with `mcq-` during the build process                                                                     |
| numbered      | `flag`         | If present, this question will be numbered with CSS `counter()`.                                                                                                               |
| show_feedback | `flag`         | If present, this question will be made into an interactive UI component that will allow students to check their chosen answer and get feedback on whether it's right or wrong. |
