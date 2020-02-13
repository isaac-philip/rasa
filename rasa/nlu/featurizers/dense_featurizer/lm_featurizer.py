import numpy as np
from typing import Any, Optional, Text

from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.featurizers.featurizer import Featurizer
from rasa.nlu.training_data import Message, TrainingData

from rasa.nlu.constants import (
    TEXT,
    LANGUAGE_MODEL_DOCS,
    DENSE_FEATURE_NAMES,
    DENSE_FEATURIZABLE_ATTRIBUTES,
    TOKENS_NAMES,
    SEQUENCE_FEATURES,
    SENTENCE_FEATURES,
)


class LanguageModelFeaturizer(Featurizer):

    provides = [
        DENSE_FEATURE_NAMES[attribute] for attribute in DENSE_FEATURIZABLE_ATTRIBUTES
    ]

    requires = [
        LANGUAGE_MODEL_DOCS[attribute] for attribute in DENSE_FEATURIZABLE_ATTRIBUTES
    ] + [TOKENS_NAMES[attribute] for attribute in DENSE_FEATURIZABLE_ATTRIBUTES]

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:

        for example in training_data.training_examples:
            for attribute in DENSE_FEATURIZABLE_ATTRIBUTES:
                self._set_lm_features(example, attribute)

    def get_doc(self, message: Message, attribute: Text) -> Any:

        return message.get(LANGUAGE_MODEL_DOCS[attribute])

    def process(self, message: Message, **kwargs: Any) -> None:

        self._set_lm_features(message)

    def _set_lm_features(self, message: Message, attribute: Text = TEXT):
        """Adds the precomputed word vectors to the messages features."""

        doc = self.get_doc(message, attribute)

        if doc is not None:
            sequence_features = doc[SEQUENCE_FEATURES]
            sentence_features = doc[SENTENCE_FEATURES]

            features = np.concatenate([sequence_features, sentence_features])

            features = self._combine_with_existing_dense_features(
                message, features, DENSE_FEATURE_NAMES[attribute]
            )
            message.set(DENSE_FEATURE_NAMES[attribute], features)
