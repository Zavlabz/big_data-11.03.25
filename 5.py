from typing import List


def find_maximal_subarray_sum(nums: List[int], k: int) -> int:
    if not nums:
        return 0  # массив пуст

    n = len(nums)
    max_sum = float('-inf')

    # все возмож подмассив
    for length in range(1, min(k, n) + 1):
        current_sum = sum(nums[:length])
        window_max = current_sum

        for i in range(length, n):
            current_sum += nums[i] - nums[i - length]
            window_max = max(window_max, current_sum)
        max_sum = max(max_sum, window_max)
    return max_sum

if __name__ == "__main__":
    nums = [55, 34, -1344, 34243, 23235, 11113, 236, 3237]
    k = 2
    result = find_maximal_subarray_sum(nums, k)
    print(result)
