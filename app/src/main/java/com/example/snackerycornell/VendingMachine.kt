package com.example.snackerycornell

data class VendingMachine(
    val id: Int,
    val name: String,
    val location: String,
    val imageResourceId: Int,
    val isOpen: Boolean
)
