// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include "onnxruntime_cxx_api.h"
#include <iostream>
#include <map>
#include <msgpack.hpp>

namespace msgpack {
MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS) {
    namespace adaptor {

    std::tuple<std::string, std::vector<int64_t>> GetTensorTypeAndShape(msgpack::object const& o) {
        uint32_t map_size = o.via.map.size;

        std::string tensor_type;
        std::vector<int64_t> tensor_shape;
        for (uint32_t i = 0; i < map_size; i++) {
            msgpack::object_kv& obj = o.via.map.ptr[i];
            msgpack::object& key = obj.key;
            msgpack::object& val = obj.val;
            if (key.type != msgpack::type::BIN) {
                throw msgpack::type_error();
            }
            std::vector<char> key_chars = key.as<std::vector<char>>();
            std::string key_str(key_chars.begin(), key_chars.end());
            if (key_str == "type") {
                tensor_type = val.as<std::string>();
            } else if (key_str == "shape") {
                tensor_shape = val.as<std::vector<int64_t>>();
            }
        }

        return std::make_tuple(tensor_type, tensor_shape);
    }

    int64_t GetTensorElementCount(std::vector<int64_t>& tensor_shape) {
        size_t len = tensor_shape.size();
        if (len == 0 || (len == 1 && tensor_shape[0] == 1)) {
            return 1;
        }
        int64_t size = 1;
        for (size_t i = 0; i < len; i++) {
            size *= tensor_shape[i];
        }
        return size;
    }

    template<typename T>
    Ort::Value CreateTensorWithDataAndShape(msgpack::object& val, std::vector<int64_t>& tensor_shape) {
        if (val.type != msgpack::type::BIN) {
            throw msgpack::type_error();
        }

        Ort::MemoryInfo info("Cpu", OrtDeviceAllocator, 0, OrtMemTypeDefault);
        T* tensor_ptr = reinterpret_cast<T*>(const_cast<char*>(val.via.bin.ptr));
        int64_t tensor_element_count = GetTensorElementCount(tensor_shape);

        return Ort::Value::CreateTensor<T>(info, tensor_ptr, tensor_element_count, tensor_shape.data(), tensor_shape.size());
    }

    std::tuple<const char*, int64_t> GetBinDataAndSize(Ort::Value const& v) {
        Ort::TensorTypeAndShapeInfo info = v.GetTensorTypeAndShapeInfo();
        ONNXTensorElementDataType type = info.GetElementType();
        size_t element_count = info.GetElementCount();
        switch (type) {
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<float>()), element_count * sizeof(float));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_DOUBLE:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<double>()), element_count * sizeof(double));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT8:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::int8_t>()), element_count * sizeof(std::int8_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT16:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::int16_t>()), element_count * sizeof(std::int16_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT32:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::int32_t>()), element_count * sizeof(std::int32_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT64:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::int64_t>()), element_count * sizeof(std::int64_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT8:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::uint8_t>()), element_count * sizeof(std::uint8_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT16:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::uint16_t>()), element_count * sizeof(std::uint16_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT32:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::uint32_t>()), element_count * sizeof(std::uint32_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT64:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<std::uint64_t>()), element_count * sizeof(std::uint64_t));
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_BOOL:
                return std::make_tuple(reinterpret_cast<const char*>(v.GetTensorData<bool>()), element_count * sizeof(bool));
                break;
            default:
                std::string error_msg = "Tensor type is not supported by model-perf-toolkit now.";
                throw std::runtime_error(error_msg);
                break;
        }
    }

    std::string GetElementTypeStr(ONNXTensorElementDataType& type) {
        switch (type) {
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT:
                return "<f4";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_DOUBLE:
                return "<f8";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT8:
                return "<i1";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT16:
                return "<i2";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT32:
                return "<i4";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_INT64:
                return "<i8";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT8:
                return "<u1";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT16:
                return "<u2";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT32:
                return "<u4";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT64:
                return "<u8";
                break;
            case ONNXTensorElementDataType::ONNX_TENSOR_ELEMENT_DATA_TYPE_BOOL:
                return "<b1";
                break;
            default:
                return "unsupported";
                break;
        }
    }

    template<>
    struct as<Ort::Value> {
        Ort::Value operator()(msgpack::object const& o) const {
            // parse map to tensor, follow the format here: https://github.com/lebedov/msgpack-numpy/blob/fd7032a3045f268f84d26baa7cc9fb7f3cfec99d/msgpack_numpy.py#L84
            if (o.type != msgpack::type::MAP) {
                throw msgpack::type_error();
            }
            if (o.via.map.size != 5) {
                throw msgpack::type_error();
            }
            uint32_t map_size = o.via.map.size;

            std::tuple<std::string, std::vector<int64_t>> type_and_shape = GetTensorTypeAndShape(o);
            std::string& tensor_type_str = std::get<0>(type_and_shape);
            std::vector<int64_t>& tensor_shape = std::get<1>(type_and_shape);

            // create tensor with data in msgpack::object
            for (uint32_t i = 0; i < map_size; i++) {
                msgpack::object_kv& obj = o.via.map.ptr[i];
                if (obj.key.type != msgpack::type::BIN) {
                    throw msgpack::type_error();
                }

                std::vector<char> key_chars = obj.key.as<std::vector<char>>();
                std::string key_str(key_chars.begin(), key_chars.end());

                if (key_str != "data") {
                    continue;
                }
                if (obj.val.type != msgpack::type::BIN) {
                    throw msgpack::type_error();
                }

                // float32
                if (tensor_type_str.find("f4") != std::string::npos) {
                    return CreateTensorWithDataAndShape<float>(obj.val, tensor_shape);
                }
                // float64
                else if (tensor_type_str.find("f8") != std::string::npos) {
                    return CreateTensorWithDataAndShape<double>(obj.val, tensor_shape);
                }
                // int8
                else if (tensor_type_str.find("i1") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::int8_t>(obj.val, tensor_shape);
                }
                // int16
                else if (tensor_type_str.find("i2") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::int16_t>(obj.val, tensor_shape);
                }
                // int32
                else if (tensor_type_str.find("i4") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::int32_t>(obj.val, tensor_shape);
                }
                // int64
                else if (tensor_type_str.find("i8") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::int64_t>(obj.val, tensor_shape);
                }
                // uint8
                else if (tensor_type_str.find("u1") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::uint8_t>(obj.val, tensor_shape);
                }
                // uint16
                else if (tensor_type_str.find("u2") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::uint16_t>(obj.val, tensor_shape);
                }
                // uint32
                else if (tensor_type_str.find("u4") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::uint32_t>(obj.val, tensor_shape);
                }
                // uint64
                else if (tensor_type_str.find("u8") != std::string::npos) {
                    return CreateTensorWithDataAndShape<std::uint64_t>(obj.val, tensor_shape);
                }
                // bool
                else if (tensor_type_str.find("b1") != std::string::npos) {
                    return CreateTensorWithDataAndShape<bool>(obj.val, tensor_shape);
                }
                // not supported type
                else {
                    std::string error_msg = "Tensor type: " + tensor_type_str + " is not supported by model-perf-toolkit now.";
                    throw std::runtime_error(error_msg);
                }
            }

            return Ort::Value{ nullptr };
        }
    };

    template<>
    struct pack<Ort::Value> {
        template<typename Stream>
        packer<Stream>& operator()(msgpack::packer<Stream>& o, Ort::Value const& v) const {
            // pack tensor as map, follow the format here: https://github.com/lebedov/msgpack-numpy/blob/fd7032a3045f268f84d26baa7cc9fb7f3cfec99d/msgpack_numpy.py#L54
            o.pack_map(5);

            std::string key1("nd");
            o.pack_bin(key1.size());
            o.pack_bin_body(key1.c_str(), key1.size());
            o.pack(true);

            std::string key2("type");
            o.pack_bin(key2.size());
            o.pack_bin_body(key2.c_str(), key2.size());
            Ort::TensorTypeAndShapeInfo info = v.GetTensorTypeAndShapeInfo();
            ONNXTensorElementDataType type = info.GetElementType();
            std::string type_str = GetElementTypeStr(type);
            o.pack_str(type_str.size());
            o.pack_str_body(type_str.c_str(), type_str.size());

            std::string key3("kind");
            o.pack_bin(key3.size());
            o.pack_bin_body(key3.c_str(), key3.size());
            std::string kind_str("");
            o.pack_bin(kind_str.size());
            o.pack_bin_body(kind_str.c_str(), kind_str.size());

            std::string key4("shape");
            o.pack_bin(key4.size());
            o.pack_bin_body(key4.c_str(), key4.size());
            std::vector<int64_t> shape = info.GetShape();
            o.pack(shape);

            std::string key5("data");
            o.pack_bin(key5.size());
            o.pack_bin_body(key5.c_str(), key5.size());
            std::tuple<const char*, int64_t> data = GetBinDataAndSize(v);
            const char* output_data = std::get<0>(data);
            const int64_t size = std::get<1>(data);
            o.pack_bin(size);
            o.pack_bin_body(output_data, size);

            return o;
        }
    };

    } // namespace adaptor
} // MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS)
} // namespace msgpack
