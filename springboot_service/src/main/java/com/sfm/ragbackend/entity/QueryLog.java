package com.sfm.ragbackend.entity;

import jakarta.persistence.*;

import java.time.LocalDateTime;

/**
 * One row per question asked. This is the traceability/audit log from
 * the project architecture doc — every answer is logged with which
 * sources it cited, so answers stay auditable, not a black box.
 *
 * Getters/setters written by hand instead of via Lombok — Lombok
 * 1.18.34 doesn't reliably generate methods on very new JDKs (JDK 25)
 * yet, and this class is small enough that hand-writing them avoids
 * the whole toolchain-compatibility problem entirely.
 */
@Entity
@Table(name = "query_log")
public class QueryLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String question;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String answer;

    // Stored as a simple comma-separated string for now (e.g.
    // "Politique Qualité.docx, hr_leave_policy.docx"). If you need to
    // query/filter by individual source later, split this into a
    // separate QuerySource entity with a @OneToMany relationship
    // instead — not needed yet for just displaying/logging.
    @Column(columnDefinition = "TEXT")
    private String sources;

    @Column(nullable = false)
    private LocalDateTime askedAt;

    @PrePersist
    protected void onCreate() {
        this.askedAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public String getSources() {
        return sources;
    }

    public void setSources(String sources) {
        this.sources = sources;
    }

    public LocalDateTime getAskedAt() {
        return askedAt;
    }

    public void setAskedAt(LocalDateTime askedAt) {
        this.askedAt = askedAt;
    }
}