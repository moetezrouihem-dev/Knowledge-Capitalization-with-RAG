package com.sfm.ragbackend.repository;

import com.sfm.ragbackend.entity.Conversation;
import com.sfm.ragbackend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ConversationRepository extends JpaRepository<Conversation, Long> {
    List<Conversation> findByUserOrderByCreatedAtDesc(User user);
    Optional<Conversation> findByIdAndUser(Long id, User user);
}
