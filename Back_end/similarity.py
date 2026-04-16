#工具文件：实验匹配器
class ExperimentMatcher:
    def __init__(self, experiments):
        self.experiments = experiments
    
    def find_most_similar(self, user_input):
        """改进的实验匹配实现"""
        if not self.experiments:
            return None
        
        #检查实验标题是否包含用户输入的关键词
        best_match = None
        best_score = 0
        
        user_input_lower = user_input.lower()
        
        for experiment in self.experiments:
            title = experiment.get('title', '').lower()
            
            # 计算匹配得分
            score = 0
            
            # 方法1：直接子字符串匹配
            if user_input_lower in title:
                score = len(user_input_lower)
            
            # 方法2：标题在用户输入中
            elif title in user_input_lower:
                score = len(title)
            
            # 方法3：关键词匹配（检查用户输入的每个字是否都在标题中）
            elif all(char in title for char in user_input_lower):
                score = len(user_input_lower)
            
            # 方法4：部分匹配（检查用户输入的部分内容在标题中）
            else:
                # 检查用户输入的每个连续子串
                for i in range(len(user_input_lower)):
                    for j in range(i+1, len(user_input_lower)+1):
                        substring = user_input_lower[i:j]
                        if len(substring) > 1 and substring in title:
                            score = max(score, len(substring))
            
            if score > best_score:
                best_score = score
                best_match = experiment
        
        if best_match and best_score > 0:
            return {
                'experiment': best_match,
                'similarity': best_score / len(user_input_lower) if user_input_lower else 0
            }
        else:
            return None
