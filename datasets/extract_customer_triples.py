"""
从OWL/TTL文件中提取指定客户的所有三元组信息
"""
from rdflib import Graph, URIRef, RDF
from typing import Dict, Any, List, Tuple


def get_customer_triples(ttl_file_path: str, customer_id: str) -> Dict[str, Any]:
    """
    从TTL文件中提取指定客户的所有三元组信息，包括关联实体
    
    Args:
        ttl_file_path: TTL/OWL文件路径
        customer_id: 客户ID，如 "00071a2af7bd7e9a1f0b08a968c5f724"
    
    Returns:
        包含客户所有三元组信息的字典
    """
    g = Graph()
    g.parse(ttl_file_path, format='turtle')
    
    customer_uri = URIRef(f"http://example.org/insurance/customer/{customer_id}")
    
    if (customer_uri, None, None) not in g:
        return {
            "error": f"客户 {customer_id} 不存在",
            "customer_uri": str(customer_uri),
            "customer_triples": [],
            "related_entities": {},
            "all_triples": []
        }
    
    result = {
        "customer_uri": str(customer_uri),
        "customer_triples": [],
        "related_entities": {},
        "all_triples": []
    }
    
    # 获取客户直接属性的三元组
    for s, p, o in g.triples((customer_uri, None, None)):
        triple = {
            "subject": str(s),
            "predicate": str(p),
            "object": str(o),
            "object_type": type(o).__name__
        }
        result["customer_triples"].append(triple)
        result["all_triples"].append(triple)
        
        # 如果对象是URI引用，且不是rdf:type，说明是关联实体，需要获取其属性
        if isinstance(o, URIRef) and p != RDF.type:
            entity_uri = o
            uri_str = str(entity_uri)
            
            # 提取实体类型
            if '/app_event/' in uri_str:
                entity_type = 'app_event'
            elif '/wechat_msg/' in uri_str:
                entity_type = 'wechat_msg'
            elif '/product/' in uri_str:
                entity_type = 'product'
            else:
                entity_type = uri_str.split('/')[-2]
            
            if entity_type not in result["related_entities"]:
                result["related_entities"][entity_type] = []
            
            # 获取关联实体的所有属性三元组
            entity_triples = []
            for es, ep, eo in g.triples((entity_uri, None, None)):
                triple = {
                    "subject": str(es),
                    "predicate": str(ep),
                    "object": str(eo),
                    "object_type": type(eo).__name__
                }
                entity_triples.append(triple)
                result["all_triples"].append(triple)
            
            result["related_entities"][entity_type].append({
                "entity_uri": str(entity_uri),
                "triples": entity_triples
            })
    
    return result


def print_customer_triples(result: Dict[str, Any]) -> None:
    """格式化打印客户三元组信息"""
    if "error" in result:
        print(f"错误: {result['error']}")
        return
    
    print(f"客户URI: {result['customer_uri']}")
    print("=" * 80)
    
    # 打印客户直接属性
    print(f"\n【客户属性】共 {len(result['customer_triples'])} 个三元组:")
    print("-" * 80)
    for triple in result["customer_triples"]:
        pred = triple["predicate"].split('#')[-1] if '#' in triple["predicate"] else triple["predicate"]
        obj = triple["object"]
        print(f"  {pred}: {obj}")
    
    # 打印关联实体
    for entity_type, entities in result["related_entities"].items():
        print(f"\n【关联实体 - {entity_type}】共 {len(entities)} 个:")
        print("-" * 80)
        for entity in entities:
            print(f"  URI: {entity['entity_uri']}")
            if entity["triples"]:
                for triple in entity["triples"]:
                    pred = triple["predicate"].split('#')[-1] if '#' in triple["predicate"] else triple["predicate"]
                    obj = triple["object"]
                    print(f"    {pred}: {obj}")
            else:
                print(f"    (无属性定义)")
    
    print("\n" + "=" * 80)
    print(f"总计: {len(result['all_triples'])} 个三元组")


def get_triples_as_list(ttl_file_path: str, customer_id: str) -> List[Tuple[str, str, str]]:
    """
    获取客户所有三元组的简单列表格式
    
    Returns:
        三元组列表，每个元素为 (主语, 谓词, 宾语) 元组
    """
    result = get_customer_triples(ttl_file_path, customer_id)
    if "error" in result:
        return []
    return [(t["subject"], t["predicate"], t["object"]) for t in result["all_triples"]]


if __name__ == "__main__":
    ttl_file = r"E:\项目\数智本体2\本体模型\带规则版_data.ttl"
    customer_id = "00071a2af7bd7e9a1f0b08a968c5f724"
    
    print(f"正在查询客户: {customer_id}\n")
    
    result = get_customer_triples(ttl_file, customer_id)
    print_customer_triples(result)
