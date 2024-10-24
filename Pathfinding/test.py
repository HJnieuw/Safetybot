schedule = [0, 3, 1, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2]

print("Original Schedule:", schedule)

def remove_exact_duplicates(lst):
    if not lst:
        return []  # Handle empty list case
    result = [lst[0]]  # Start with the first element
    
    for i in range(1, len(lst)):
        # Only append if current element is different from the previous one
        if lst[i] != lst[i-1]:
            result.append(lst[i])
    
    return result

newschedule = remove_exact_duplicates(schedule)

print("New Schedule", newschedule)