from typing import List


class Group:
    def __init__(self, group_id: int, name: str, description: str, 
                 members_count: int):
        self.id = group_id
        self.name = name
        self.description = description
        self.members_count = members_count

class SubscriptionList:
    def __init__(self, groups: List[Group]):
        self.groups = groups

def parse_vk_subscriptions(vk_json: dict, group_number: int = -1) -> SubscriptionList:
    groups_data = vk_json.get("response", {}).get("items", [])
    groups = []
    
    for group in groups_data:
        groups.append(Group(
            group_id=group.get("id", 0),
            name=group.get("name", ""),
            description=group.get("description", "")[:100] + "..." if group.get("description") else "",
            members_count=group.get("members_count", 0),
        ))
    
    return SubscriptionList(groups[:group_number] if group_number > 0 else groups)

def subscriptions_to_prompt(sub_list: SubscriptionList, question: str) -> str:
    subs_text = "\n\n".join(
        f"[Сообщество {group.name}]\n"
        f"Участников: {group.members_count}\n" 
        f"Описание: {group.description}\n"
        for group in sub_list.groups
    )
    return f"Список подписок:\n\n{subs_text}\n\n{question}"