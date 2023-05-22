# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from perftools.logger import logger
from perftools.dataset.squad import SQuAD
from perftools.dataset.dataset import DataSet


class DataSetFactory:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def create_hf_transformer_inputs(self, model_name: str):
        from transformers.models.auto import AutoFeatureExtractor, AutoProcessor, AutoTokenizer

        preprocessor = AutoTokenizer.from_pretrained(model_name)
        squad_v2 = SQuAD(self.cache_dir)
        inputs = []
        total_tokens = 0
        for q in squad_v2.get_questions():
            tensor_input = dict(preprocessor(q, return_tensors='pt'))
            numpy_input = {}
            for k, v in tensor_input.items():
                numpy_input[k] = v.cpu().detach().numpy()
            inputs.append({'output_names': None, 'input_feed': numpy_input})
            total_tokens += tensor_input['input_ids'].size(dim=1)
        logger.info(f'number of queries: {len(inputs)}, avg number of tokens: {total_tokens / len(inputs):.2f}')
        return inputs

    def create_bert(self, model_name: str = 'bert-base-uncased'):
        inputs = self.create_hf_transformer_inputs(model_name)
        return DataSet(inputs, None)

    def create_albert(self, model_name: str = 'albert-base-v2'):
        """
        References:
        * https://huggingface.co/albert-base-v2
        """

        inputs = self.create_hf_transformer_inputs(model_name)
        return DataSet(inputs, None)

    def create_gpt2(self, model_name: str = 'gpt2'):
        """
        References:
        * https://huggingface.co/albert-base-v2
        """

        inputs = self.create_hf_transformer_inputs(model_name)
        return DataSet(inputs, None)

    def create_t5_encoder(self, model_name: str):
        """
        References:
        * https://huggingface.co/docs/transformers/glossary#decoder-input-ids
        """

        from transformers import T5Config, T5EncoderModel, T5Tokenizer

        preprocessor = T5Tokenizer.from_pretrained(model_name)
        squad_v2 = SQuAD(self.cache_dir)
        inputs = []
        total_tokens = 0
        for q in squad_v2.get_questions():
            tensor_input = dict(preprocessor(q, return_tensors='pt'))
            numpy_input = {}
            for k, v in tensor_input.items():
                numpy_input[k] = v.cpu().detach().numpy()
            inputs.append({'output_names': None, 'input_feed': numpy_input})
            total_tokens += tensor_input['input_ids'].size(dim=1)
        logger.info(f'number of queries: {len(inputs)}, avg number of tokens: {total_tokens / len(inputs):.2f}')

        return DataSet(inputs, None)
